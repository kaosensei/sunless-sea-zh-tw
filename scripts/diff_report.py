#!/usr/bin/env python3
"""
產生 OpenCC 轉換前後的差異報告，供人工審閱。
每個 JSON 檔案輸出一份 docs/diff/*.md。

用法：
  python3 scripts/diff_report.py [source_dir] [trans_dir]
"""

import json
import sys
from pathlib import Path

TEXT_FIELDS = {
    'Name', 'Description', 'Teaser', 'ButtonText',
    'ExoticEffects', 'ChangeDescriptionText', 'LevelDescriptionText',
    'EnhancementsDescription', 'SaleDescription', 'BuyMessage', 'SellMessage',
    'LevelImageText',
}


def collect_texts(obj, path=''):
    texts = {}
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            texts.update(collect_texts(item, f"{path}[{i}]"))
    elif isinstance(obj, dict):
        entry_id = obj.get('Id', '')
        id_str = f"#{entry_id}" if entry_id else ''
        for k, v in obj.items():
            if k in TEXT_FIELDS and isinstance(v, str) and v.strip():
                texts[f"{path}{id_str}.{k}"] = v
            elif isinstance(v, (dict, list)):
                texts.update(collect_texts(v, f"{path}{id_str}.{k}"))
    return texts


def diff_file(src_path, trans_path):
    with open(src_path, encoding='utf-8') as f:
        src_data = json.load(f)
    with open(trans_path, encoding='utf-8') as f:
        trans_data = json.load(f)

    src_texts = collect_texts(src_data)
    trans_texts = collect_texts(trans_data)

    diffs = []
    for key in src_texts:
        sc = src_texts.get(key, '')
        tc = trans_texts.get(key, sc)
        if sc != tc:
            diffs.append((key, sc, tc))
    return diffs


def main():
    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('source/vanilla')
    trans_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('translations/vanilla')
    out_dir = Path('docs/diff')
    out_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(trans_dir.rglob('*.json'))
    total_diffs = 0

    for trans_path in json_files:
        rel = trans_path.relative_to(trans_dir)
        src_path = source_dir / rel
        if not src_path.exists():
            continue

        diffs = diff_file(src_path, trans_path)
        total_diffs += len(diffs)

        out_path = out_dir / rel.with_suffix('.md')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"# Diff: {rel}\n\n")
            f.write(f"OpenCC 轉換變動：{len(diffs)} 處\n\n")
            for key, sc, tc in diffs[:200]:
                f.write(f"### `{key}`\n")
                f.write(f"- 簡：{sc[:300]}\n")
                f.write(f"- 繁：{tc[:300]}\n\n")

        print(f"  {rel}：{len(diffs)} 處變動 → {out_path}")

    print(f"\n合計 {total_diffs} 處變動")


if __name__ == '__main__':
    main()
