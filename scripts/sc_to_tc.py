#!/usr/bin/env python3
"""
批次將 source/ 的簡中 JSON 轉換為繁中，輸出到 translations/。

用法：
  python3 scripts/sc_to_tc.py [source_dir] [output_dir]
  預設：source/vanilla → translations/vanilla
"""

import json
import sys
from pathlib import Path

import opencc

# 需要翻譯的文字欄位（白名單）
TEXT_FIELDS = {
    'Name', 'Description', 'Teaser', 'ButtonText',
    'ExoticEffects', 'ChangeDescriptionText', 'LevelDescriptionText',
    'EnhancementsDescription', 'SaleDescription', 'BuyMessage', 'SellMessage',
    'LevelImageText',
}


def load_protected(glossary_dir='glossary'):
    path = Path(glossary_dir) / 'protected.json'
    if not path.exists():
        return set()
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return {item['id'] for item in data}


def load_terms(glossary_dir='glossary'):
    """載入自定義詞庫，返回 {簡中: 繁中} 對應表。"""
    path = Path(glossary_dir) / 'terms.json'
    if not path.exists():
        return {}
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return {item['sc']: item['tc'] for item in data if item.get('sc') and item.get('tc')}


def convert_text(text, converter, terms):
    if not isinstance(text, str) or not text.strip():
        return text
    result = converter.convert(text)
    for sc, tc in terms.items():
        result = result.replace(sc, tc)
    return result


def convert_obj(obj, converter, terms, protected_ids, current_id=None):
    if isinstance(obj, list):
        return [convert_obj(item, converter, terms, protected_ids) for item in obj]

    if isinstance(obj, dict):
        entry_id = obj.get('Id', current_id)
        result = {}
        for k, v in obj.items():
            if k in TEXT_FIELDS and isinstance(v, str):
                # 受保護的 ID 跳過 Name 欄位轉換
                if k == 'Name' and entry_id in protected_ids:
                    result[k] = v
                else:
                    result[k] = convert_text(v, converter, terms)
            elif isinstance(v, (dict, list)):
                result[k] = convert_obj(v, converter, terms, protected_ids, entry_id)
            else:
                result[k] = v
        return result

    return obj


def convert_file(src_path, dst_path, converter, terms, protected_ids):
    with open(src_path, encoding='utf-8') as f:
        data = json.load(f)

    converted = convert_obj(data, converter, terms, protected_ids)

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_path, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)

    return len(data) if isinstance(data, list) else 1


def main():
    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('source/vanilla')
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('translations/vanilla')

    print(f"來源：{source_dir}")
    print(f"輸出：{output_dir}\n")

    converter = opencc.OpenCC('s2twp')
    terms = load_terms()
    protected_ids = load_protected()

    print(f"受保護 ID：{len(protected_ids)} 個")
    print(f"自定義詞庫：{len(terms)} 條\n")

    json_files = sorted(source_dir.rglob('*.json'))
    print(f"找到 {len(json_files)} 個 JSON 檔案\n")

    total = 0
    for src in json_files:
        rel = src.relative_to(source_dir)
        dst = output_dir / rel
        count = convert_file(src, dst, converter, terms, protected_ids)
        total += count
        print(f"  ✓ {rel}  ({count} 條)")

    print(f"\n完成，共轉換 {total} 條")


if __name__ == '__main__':
    main()
