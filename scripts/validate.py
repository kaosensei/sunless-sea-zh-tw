#!/usr/bin/env python3
"""
驗證翻譯 JSON 檔案：格式正確性、條目數量、特殊字元保留。

用法：
  python3 scripts/validate.py [source_dir] [trans_dir]
  預設：source/vanilla vs translations/vanilla
"""

import json
import re
import sys
from pathlib import Path

SPECIAL_CHAR_RE = re.compile(r'\\[ntr"\\]')


def find_specials(text):
    return set(SPECIAL_CHAR_RE.findall(text))


def check_file(src_path, trans_path):
    errors = []

    # 1. JSON 格式
    try:
        with open(trans_path, encoding='utf-8') as f:
            trans_data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"JSON 格式錯誤：{e}"]

    # 2. 條目數量
    try:
        with open(src_path, encoding='utf-8') as f:
            src_data = json.load(f)
        if isinstance(src_data, list) and isinstance(trans_data, list):
            if len(src_data) != len(trans_data):
                errors.append(
                    f"條目數不符：來源 {len(src_data)}，翻譯 {len(trans_data)}"
                )
    except Exception:
        pass

    # 3. 特殊字元保留（比對原始文字）
    try:
        src_raw = src_path.read_text(encoding='utf-8')
        trans_raw = trans_path.read_text(encoding='utf-8')
        src_specials = find_specials(src_raw)
        for sp in src_specials:
            if sp in src_raw and sp not in trans_raw:
                errors.append(f"特殊字元可能遺失：{sp!r}")
    except Exception:
        pass

    return errors


def main():
    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('source/vanilla')
    trans_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('translations/vanilla')

    json_files = sorted(trans_dir.rglob('*.json'))
    if not json_files:
        print("找不到翻譯檔案")
        sys.exit(1)

    all_passed = True
    for trans_path in json_files:
        rel = trans_path.relative_to(trans_dir)
        src_path = source_dir / rel
        errors = check_file(src_path, trans_path)
        if errors:
            all_passed = False
            print(f"  ✗ {rel}")
            for e in errors:
                print(f"      {e}")
        else:
            print(f"  ✓ {rel}")

    print()
    if all_passed:
        print("✅ 全部通過")
    else:
        print("❌ 驗證失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()
