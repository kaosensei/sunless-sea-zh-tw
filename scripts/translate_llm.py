#!/usr/bin/env python3
"""
translate_llm.py - 用 Claude API 批次翻譯英文原文到繁中

用法：
    python3 scripts/translate_llm.py entities/areas.json
    python3 scripts/translate_llm.py entities/events.json --batch-size 5
    python3 scripts/translate_llm.py entities/areas.json --dry-run

輸入：source/en/<rel_path>
輸出：translations/vanilla/<rel_path>（已翻譯的條目自動跳過，支援中斷續跑）
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import anthropic

# ── 路徑常數 ───────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
EN_DIR = BASE_DIR / "source" / "en"
OUT_DIR = BASE_DIR / "translations" / "vanilla"
GLOSSARY_DIR = BASE_DIR / "glossary"
STYLE_GUIDE = BASE_DIR / "docs" / "style-guide.md"

# ── 可翻譯欄位白名單 ───────────────────────────────────────────────────────────

TEXT_FIELDS = {
    "Name", "Description", "Teaser", "ButtonText",
    "ExoticEffects", "ChangeDescriptionText", "LevelDescriptionText",
    "EnhancementsDescription", "SaleDescription", "BuyMessage",
    "SellMessage", "LevelImageText", "MoveMessage", "HumanName", "Title",
}

# ── 術語表（系統提示用） ────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """\
你是 Sunless Sea（地獄海）的繁體中文（台灣）翻譯專家。

## 翻譯風格

**語氣**：維多利亞哥德 × 克蘇魯宇宙恐怖 × 黑色幽默混合體。

核心原則：
- 精煉優先——每個字都要有重量，不冗贅
- 語氣冷靜、帶距離感——「主體是宇宙，不是人」
- 暗示比描述有力——模糊的恐怖不要說清楚，讓讀者填空
- 黑色幽默不能翻死——輕描淡寫可怕的事，保留反差
- 現代書面語為主，關鍵意象適度文言點綴

**詞彙**：用帶古典色彩的字（幽冥、蒼茫、晦暗、深淵、詭譎、悖理、亙古）取代白話（很黑、很深、奇怪）

**人稱**：you → 你（不用您）；Captain → 船長

**標點**：全形標點。引號用「」（外層）『』（內層）。破折號用——。刪節號用……。英文單引號 ' 或雙引號 " 的對話一律改為「」。

**格式（必須保留）**：
- `<i>文字</i>`：保留標籤，翻譯內容
- `<br/>`：完整保留，不翻譯
- `[遊戲提示]`：保留方括號，翻譯內容
- `{{x}}` `{{y}}` 等佔位符：完整保留，不翻譯

## 固定術語

{terms}

## 禁翻條目

以下 ID 的 Name 欄位**不翻譯**，保留英文原文：
{protected}

## 任務格式

輸入：JSON 陣列，每個元素是一個條目，有 `id` 和需要翻譯的文字欄位。
輸出：相同結構的 JSON 陣列，只有文字欄位被翻譯成繁中，其餘欄位（id 等）不變。

只回傳 JSON，不要加任何說明文字、不要加 markdown code fence。
"""


def load_glossary():
    """載入術語表和受保護 ID。"""
    terms = []
    terms_path = GLOSSARY_DIR / "terms.json"
    if terms_path.exists():
        with open(terms_path, encoding="utf-8") as f:
            for item in json.load(f):
                if item.get("en") and item.get("tc"):
                    terms.append(f"- {item['en']} → {item['tc']}"
                                 + (f"（{item['notes']}）" if item.get("notes") else ""))

    protected_ids = set()
    protected_path = GLOSSARY_DIR / "protected.json"
    if protected_path.exists():
        with open(protected_path, encoding="utf-8") as f:
            for item in json.load(f):
                protected_ids.add(item["id"])

    return terms, protected_ids


def build_system_prompt(terms, protected_ids):
    terms_str = "\n".join(terms) if terms else "（尚無）"
    protected_str = ", ".join(str(i) for i in sorted(protected_ids)) if protected_ids else "（無）"
    return SYSTEM_PROMPT_TEMPLATE.format(terms=terms_str, protected=protected_str)


# ── 文字欄位萃取 / 合併 ─────────────────────────────────────────────────────────

def extract_text(obj, protected_ids=None, entry_id=None):
    """
    遞迴萃取需要翻譯的文字欄位，返回與原結構相同但只含文字欄位的 dict/list。
    protected_ids：這些 ID 的 Name 欄位不萃取（保留英文）。
    """
    if isinstance(obj, dict):
        current_id = obj.get("Id", entry_id)
        result = {}
        if "Id" in obj:
            result["id"] = obj["Id"]
        for k, v in obj.items():
            if k in TEXT_FIELDS and isinstance(v, str) and v.strip():
                if k == "Name" and current_id in (protected_ids or set()):
                    continue  # 跳過受保護的 Name
                result[k] = v
            elif isinstance(v, (dict, list)):
                sub = extract_text(v, protected_ids, current_id)
                if sub:
                    result[k] = sub
        return result if len(result) > (1 if "id" in result else 0) else {}

    elif isinstance(obj, list):
        results = [extract_text(item, protected_ids, entry_id) for item in obj]
        return results if any(results) else []

    return {}


def merge_translation(original, translated, protected_ids=None, entry_id=None):
    """將翻譯結果合併回原始結構。"""
    if isinstance(original, dict) and isinstance(translated, dict):
        current_id = original.get("Id", entry_id)
        result = dict(original)
        for k, v in translated.items():
            if k == "id":
                continue
            if k in original:
                if isinstance(v, str):
                    if k == "Name" and current_id in (protected_ids or set()):
                        pass  # 不覆蓋受保護的 Name
                    else:
                        result[k] = v
                elif isinstance(v, (dict, list)) and isinstance(original[k], (dict, list)):
                    result[k] = merge_translation(original[k], v, protected_ids, current_id)
        return result

    elif isinstance(original, list) and isinstance(translated, list):
        result = list(original)
        for i, trans in enumerate(translated):
            if i < len(result) and trans:
                result[i] = merge_translation(result[i], trans, protected_ids, entry_id)
        return result

    return original


# ── Claude API 呼叫 ────────────────────────────────────────────────────────────

def translate_batch(client, system_prompt, batch_payload, dry_run=False):
    """
    翻譯一批條目。
    batch_payload: list of extracted text dicts
    返回: list of translated dicts（與輸入相同結構）
    """
    if dry_run:
        print(f"    [DRY RUN] 會翻譯 {len(batch_payload)} 條")
        return batch_payload  # 原樣返回

    user_content = json.dumps(batch_payload, ensure_ascii=False, indent=2)

    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            raw = response.content[0].text.strip()

            # 移除可能的 code fence
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                raw = raw.rsplit("```", 1)[0].strip()

            return json.loads(raw)

        except json.JSONDecodeError as e:
            print(f"    JSON 解析失敗（第 {attempt+1} 次）：{e}")
            if attempt < 2:
                time.sleep(2)
        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            print(f"    Rate limit，等待 {wait}s...")
            time.sleep(wait)
        except Exception as e:
            print(f"    API 錯誤：{e}")
            if attempt < 2:
                time.sleep(5)

    print("    翻譯失敗，返回原文")
    return batch_payload


# ── 主流程 ─────────────────────────────────────────────────────────────────────

def translate_file(rel_path, batch_size=10, dry_run=False):
    src_path = EN_DIR / rel_path
    dst_path = OUT_DIR / rel_path

    if not src_path.exists():
        print(f"錯誤：找不到 {src_path}")
        sys.exit(1)

    with open(src_path, encoding="utf-8") as f:
        entries = json.load(f)

    print(f"來源：{src_path}（{len(entries)} 條）")

    # 載入已有翻譯（支援中斷續跑）
    existing = {}
    if dst_path.exists():
        with open(dst_path, encoding="utf-8") as f:
            for item in json.load(f):
                if isinstance(item, dict) and "Id" in item:
                    existing[item["Id"]] = item
        print(f"已有翻譯：{len(existing)} 條（自動跳過）")

    terms, protected_ids = load_glossary()
    system_prompt = build_system_prompt(terms, protected_ids)
    client = anthropic.Anthropic()

    translated_map = dict(existing)
    pending = [e for e in entries if isinstance(e, dict) and e.get("Id") not in existing]
    print(f"待翻譯：{len(pending)} 條，批次大小：{batch_size}\n")

    for batch_start in range(0, len(pending), batch_size):
        batch = pending[batch_start:batch_start + batch_size]
        batch_ids = [e.get("Id", "?") for e in batch]
        first_name = batch[0].get("Name", "?") if batch else "?"
        print(f"  [{batch_start+1}-{batch_start+len(batch)}/{len(pending)}] {first_name!r}...")

        # 萃取文字欄位
        payload = [extract_text(e, protected_ids) for e in batch]
        payload = [p for p in payload if p]

        # 翻譯
        translated_batch = translate_batch(client, system_prompt, payload, dry_run)

        # 合併回原始結構
        id_to_translated = {}
        for t in translated_batch:
            eid = t.get("id") or t.get("Id")
            if eid:
                id_to_translated[eid] = t

        for orig in batch:
            eid = orig.get("Id")
            trans = id_to_translated.get(eid)
            if trans:
                merged = merge_translation(orig, trans, protected_ids)
            else:
                merged = orig  # fallback 用原文
            translated_map[eid] = merged

        # 每批完成後存檔（支援中斷續跑）
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        ordered = [translated_map[e["Id"]] for e in entries
                   if isinstance(e, dict) and e.get("Id") in translated_map]
        with open(dst_path, "w", encoding="utf-8") as f:
            json.dump(ordered, f, ensure_ascii=False, indent=2)

        if not dry_run:
            time.sleep(1)  # 避免 rate limit

    total = len(translated_map)
    print(f"\n完成：{total} 條 → {dst_path}")


def main():
    parser = argparse.ArgumentParser(description="Claude API 批次翻譯 Sunless Sea 英文原文")
    parser.add_argument("file", help="相對路徑，如 entities/areas.json")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="每批翻譯條數（events 建議 5，areas/qualities 建議 10）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只跑流程，不實際呼叫 API")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        print("錯誤：請設定 ANTHROPIC_API_KEY 環境變數")
        sys.exit(1)

    translate_file(args.file, batch_size=args.batch_size, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
