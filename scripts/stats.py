#!/usr/bin/env python3
"""
統計翻譯進度，輸出 docs/status.md。

用法：
  python3 scripts/stats.py [source_dir] [trans_dir]
"""

import json
import sys
from pathlib import Path


def count_entries(data):
    if isinstance(data, list):
        return len(data)
    return 1


def main():
    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('source/vanilla')
    trans_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('translations/vanilla')

    rows = []
    total_src = 0
    total_trans = 0

    for src_path in sorted(source_dir.rglob('*.json')):
        rel = src_path.relative_to(source_dir)
        trans_path = trans_dir / rel

        with open(src_path, encoding='utf-8') as f:
            src_count = count_entries(json.load(f))

        trans_count = 0
        if trans_path.exists():
            with open(trans_path, encoding='utf-8') as f:
                trans_count = count_entries(json.load(f))

        total_src += src_count
        total_trans += trans_count
        done = '✅' if trans_count >= src_count else ('🔄' if trans_count > 0 else '⬜')
        rows.append({'file': str(rel), 'src': src_count, 'trans': trans_count, 'done': done})

    # 終端機輸出
    print(f"{'檔案':<50} {'簡中':>6} {'繁中':>6}  狀態")
    print('-' * 70)
    for r in rows:
        print(f"{r['file']:<50} {r['src']:>6} {r['trans']:>6}  {r['done']}")
    print('-' * 70)
    print(f"{'合計':<50} {total_src:>6} {total_trans:>6}")

    # 寫入 docs/status.md
    out_path = Path('docs/status.md')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# 翻譯進度\n\n")
        f.write("| 檔案 | 簡中條目 | 繁中已轉 | 狀態 |\n")
        f.write("|------|---------|---------|------|\n")
        for r in rows:
            f.write(f"| `{r['file']}` | {r['src']} | {r['trans']} | {r['done']} |\n")
        f.write(f"\n**合計：{total_trans}/{total_src}**\n")

    print(f"\n→ 已寫入 {out_path}")


if __name__ == '__main__':
    main()
