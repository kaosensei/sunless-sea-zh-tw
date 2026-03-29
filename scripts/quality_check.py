#!/usr/bin/env python3
"""
翻譯品質自動驗收腳本

用法:
  python3 scripts/quality_check.py           # 掃描全部
  python3 scripts/quality_check.py events    # 只掃 events
  python3 scripts/quality_check.py qualities # 只掃 qualities
  python3 scripts/quality_check.py tutorials # 只掃 tutorials
  python3 scripts/quality_check.py exchanges # 只掃 exchanges
  python3 scripts/quality_check.py --fix     # 掃描 + 批次修正安全項目（瀛海→海澤）

模組說明:
  A. 禁用詞彙：瀛海（應為海澤）、您（應為你）、品質（應為記錄/標記）
  B. 英文殘留：5+ 連續 ASCII 字母（排除 HTML 標籤、佔位符）
  C. 術語英文殘留：glossary/terms.json 中的英文詞彙
  D. 格式完整性：ChangeDescriptionText / LevelDescriptionText 分隔符
  E. 佔位符完整性：{x} {y} [q:...] 等在翻譯中是否保留
"""
import json
import re
import sys
from pathlib import Path

BASE = Path("/Users/chenyucheng/projects/sunless-sea-zh-tw")
FLAT_DIR = BASE / "source/en/flat"

SOURCES = {
    "events": {
        "trans": FLAT_DIR / "entities/events_translated.json",
        "flat": FLAT_DIR / "entities/events_flat.json",
    },
    "qualities": {
        "trans": FLAT_DIR / "entities/qualities_translated.json",
        "flat": FLAT_DIR / "entities/qualities_flat.json",
    },
    "tutorials": {
        "trans": FLAT_DIR / "encyclopaedia/Tutorials_translated.json",
        "flat": FLAT_DIR / "encyclopaedia/Tutorials_flat.json",
    },
    "exchanges": {
        "trans": FLAT_DIR / "entities/exchanges_translated.json",
        "flat": None,
    },
}

# A. 禁用詞彙清單
FORBIDDEN = ["瀛海", "您", "品質"]

# B. 英文殘留：合法例外 pattern（先移除再偵測）
ENGLISH_WHITELIST_RE = re.compile(
    r"</?[a-zA-Z]+\s*/?>|"   # HTML 標籤: <i>, </i>, <br/>, <br>
    r"\{[xy]\}|"              # 佔位符 {x} {y}
    r"\[q:[^\]]*\]|"          # [q:...] 佔位符
    r"\[[^\]]{1,80}\]|"       # 方括號遊戲提示（短）
    r"\b(?:DLC|StoryNexus|OK|ID|NPC|RPG)\b"  # 已知縮寫
)

# E. 佔位符 pattern
PLACEHOLDER_RE = re.compile(r"\{[xy]\}|\[q:[^\]]+\]|\{[^}]+\}")


def load_json(path):
    if path is None or not Path(path).exists():
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def extract_fields(entry):
    """萃取一筆資料中所有需要檢查的文字欄位，回傳 [(field_path, value)]"""
    results = []
    top_fields = [
        "Name", "Description", "ChangeDescriptionText", "LevelDescriptionText",
        "LevelImageText", "ButtonText", "ExoticEffects", "EnhancementsDescription",
        "SaleDescription", "BuyMessage", "SellMessage", "Title", "Teaser",
    ]
    for f in top_fields:
        v = entry.get(f)
        if v and isinstance(v, str):
            results.append((f, v))

    # ChildBranches（events 結構）
    for branch in entry.get("ChildBranches", []):
        bid = branch.get("Id", "?")
        for f in ["Name", "Description", "ButtonText"]:
            v = branch.get(f)
            if v and isinstance(v, str):
                results.append((f"ChildBranches[{bid}].{f}", v))
        de = branch.get("DefaultEvent")
        if de:
            for f in ["Name", "Description"]:
                v = de.get(f)
                if v and isinstance(v, str):
                    results.append((f"ChildBranches[{bid}].DefaultEvent.{f}", v))

    # Shops（exchanges 結構）
    for i, shop in enumerate(entry.get("Shops", [])):
        for f in ["Name", "Description"]:
            v = shop.get(f)
            if v and isinstance(v, str):
                results.append((f"Shops[{i}].{f}", v))

    return results


def context_snippet(text, word, ctx=20):
    idx = text.find(word)
    if idx == -1:
        return text[:60]
    start = max(0, idx - ctx)
    end = min(len(text), idx + len(word) + ctx)
    snip = text[start:end]
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{snip}{suffix}"


def entry_id(entry):
    return entry.get("Id", entry.get("_index", "?"))


# ===== A. 禁用詞彙 =====

def check_forbidden(data, src):
    hits = []
    for entry in data:
        eid = entry_id(entry)
        for field, value in extract_fields(entry):
            for word in FORBIDDEN:
                if word in value:
                    hits.append((src, eid, field, word, context_snippet(value, word)))
    return hits


# ===== B. 英文殘留 =====

def check_english_residue(data, src, min_len=5):
    hits = []
    for entry in data:
        eid = entry_id(entry)
        for field, value in extract_fields(entry):
            cleaned = ENGLISH_WHITELIST_RE.sub("", value)
            matches = re.findall(r"[a-zA-Z]{" + str(min_len) + r",}", cleaned)
            if matches:
                hits.append((src, eid, field, matches, value[:100]))
    return hits


# ===== C. 術語英文殘留 =====

def load_glossary_terms():
    data = load_json(BASE / "glossary/terms.json")
    if not data:
        return []
    # 跳過有特殊語境規則的詞（London 在歷史語境下合法）
    skip = {"London (pre-Fall)", "zee", "London"}
    terms = []
    for item in data:
        en = item.get("en", "")
        if len(en) >= 4 and en not in skip:
            terms.append((en, item.get("tc", "")))
    return terms


def check_glossary_residue(data, src, terms):
    hits = []
    for entry in data:
        eid = entry_id(entry)
        for field, value in extract_fields(entry):
            for en_term, tc_term in terms:
                if re.search(re.escape(en_term), value, re.IGNORECASE):
                    hits.append((src, eid, field, en_term, tc_term,
                                 context_snippet(value, en_term)))
    return hits


# ===== D. 格式完整性 =====

def check_format_integrity(trans_data, flat_data, src):
    hits = []
    if not flat_data:
        return hits
    flat_by_id = {item["Id"]: item for item in flat_data if "Id" in item}
    format_fields = ["ChangeDescriptionText", "LevelDescriptionText"]

    for entry in trans_data:
        eid = entry.get("Id")
        if eid not in flat_by_id:
            continue  # server-only，無 flat 對比
        orig = flat_by_id[eid]

        for field in format_fields:
            orig_val = orig.get(field) or ""
            trans_val = entry.get(field) or ""
            if not orig_val:
                continue

            orig_pipes = orig_val.count("|")
            orig_tildes = orig_val.count("~")
            trans_pipes = trans_val.count("|")
            trans_tildes = trans_val.count("~")

            if orig_pipes != trans_pipes or orig_tildes != trans_tildes:
                hits.append((
                    src, eid, field,
                    f"|={orig_pipes} ~={orig_tildes}",
                    f"|={trans_pipes} ~={trans_tildes}",
                    trans_val[:100] or "(空)"
                ))
    return hits


# ===== E. 佔位符完整性 =====

def check_placeholders(trans_data, flat_data, src):
    hits = []
    if not flat_data:
        return hits
    flat_by_id = {item["Id"]: item for item in flat_data if "Id" in item}
    check_fields = ["Name", "Description", "ChangeDescriptionText", "LevelDescriptionText"]

    for entry in trans_data:
        eid = entry.get("Id")
        if eid not in flat_by_id:
            continue
        orig = flat_by_id[eid]

        for field in check_fields:
            orig_val = orig.get(field) or ""
            trans_val = entry.get(field) or ""
            orig_ph = set(PLACEHOLDER_RE.findall(orig_val))
            trans_ph = set(PLACEHOLDER_RE.findall(trans_val))
            missing = orig_ph - trans_ph
            if missing:
                hits.append((src, eid, field, sorted(missing), trans_val[:100]))
    return hits


# ===== 批次修正 =====

def fix_yinghai(path):
    """安全修正：瀛海→海澤"""
    text = Path(path).read_text(encoding="utf-8")
    count = text.count("瀛海")
    if count == 0:
        return 0
    Path(path).write_text(text.replace("瀛海", "海澤"), encoding="utf-8")
    return count


# ===== 主程式 =====

def run_checks(source_names, fix_mode=False):
    terms = load_glossary_terms()
    all_a, all_b, all_c, all_d, all_e = [], [], [], [], []

    for name in source_names:
        cfg = SOURCES[name]
        trans_data = load_json(cfg["trans"])
        flat_data = load_json(cfg["flat"])

        if trans_data is None:
            print(f"[跳過] {name}：找不到 {cfg['trans']}")
            continue

        print(f"掃描 {name}（{len(trans_data)} 筆）...")
        all_a.extend(check_forbidden(trans_data, name))
        all_b.extend(check_english_residue(trans_data, name))
        all_c.extend(check_glossary_residue(trans_data, name, terms))
        all_d.extend(check_format_integrity(trans_data, flat_data, name))
        all_e.extend(check_placeholders(trans_data, flat_data, name))

    sep = "=" * 72

    print(f"\n{sep}")
    print("=== A. 禁用詞彙 ===")
    for src, eid, field, word, snip in all_a:
        print(f"  [{src}] Id={eid}  {field}  『{word}』→ {snip}")
    by_word = {}
    for _, _, _, word, _ in all_a:
        by_word[word] = by_word.get(word, 0) + 1
    summary_a = " | ".join(f"{w}={c}" for w, c in by_word.items()) if by_word else "無"
    print(f"  總計：{len(all_a)} 處 ({summary_a})")

    print("\n=== B. 英文殘留（5+ 連續字母）===")
    for src, eid, field, matches, preview in all_b:
        print(f"  [{src}] Id={eid}  {field}  {matches}")
        print(f"         {preview[:80]}")
    print(f"  總計：{len(all_b)} 處")

    print("\n=== C. 術語英文殘留 ===")
    for src, eid, field, en_term, tc_term, snip in all_c:
        print(f"  [{src}] Id={eid}  {field}  '{en_term}'（應為「{tc_term}」）")
        print(f"         {snip}")
    print(f"  總計：{len(all_c)} 處")

    print("\n=== D. ChangeDescriptionText / LevelDescriptionText 格式 ===")
    for src, eid, field, orig_info, trans_info, preview in all_d:
        print(f"  [{src}] Id={eid}  {field}")
        print(f"         原文: {orig_info}  翻譯: {trans_info}")
        print(f"         {preview}")
    print(f"  總計：{len(all_d)} 處")

    print("\n=== E. 佔位符完整性 ===")
    for src, eid, field, missing, preview in all_e:
        print(f"  [{src}] Id={eid}  {field}  缺少 {missing}")
        print(f"         {preview}")
    print(f"  總計：{len(all_e)} 處")

    print(f"\n{sep}")
    print(f"總結  A={len(all_a)}  B={len(all_b)}  C={len(all_c)}  D={len(all_d)}  E={len(all_e)}")

    if fix_mode:
        print(f"\n{sep}")
        print("=== 執行批次修正（瀛海→海澤）===")
        total = 0
        for name in source_names:
            cfg = SOURCES[name]
            if cfg["trans"].exists():
                n = fix_yinghai(cfg["trans"])
                if n:
                    print(f"  {cfg['trans'].name}：替換 {n} 處")
                else:
                    print(f"  {cfg['trans'].name}：無需修正")
                total += n
        print(f"  共修正 {total} 處")
        if total:
            print("  → 請執行 python3 scripts/merge_translations.py all 重新合併部署")


if __name__ == "__main__":
    args = sys.argv[1:]
    fix_mode = "--fix" in args
    args = [a for a in args if not a.startswith("--")]

    valid = list(SOURCES.keys())
    if not args:
        source_names = valid
    else:
        source_names = []
        for a in args:
            if a in SOURCES:
                source_names.append(a)
            else:
                print(f"未知來源：{a}。可用：{', '.join(valid)}")
                sys.exit(1)

    run_checks(source_names, fix_mode=fix_mode)
