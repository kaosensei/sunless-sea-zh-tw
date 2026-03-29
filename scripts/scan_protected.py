#!/usr/bin/env python3
"""掃描 qualities.json，找出不能翻譯的技術性字串（船艙槽位等），輸出 glossary/protected.json。"""

import json
import sys
from pathlib import Path

# 船艙槽位名稱：這些 quality Name 被遊戲引擎直接引用，絕對不能翻譯
SLOT_NAMES = {'Forward', 'Deck', 'Aft', 'Engines', 'Bridge', 'Auxiliary'}

def scan(source_dir: Path):
    qualities_path = source_dir / 'entities' / 'qualities.json'
    with open(qualities_path, encoding='utf-8') as f:
        data = json.load(f)

    protected = []
    for item in data:
        name = item.get('Name', '')
        is_slot = item.get('IsSlot', False)
        if name in SLOT_NAMES or is_slot:
            protected.append({
                'id': item['Id'],
                'name': name,
                'reason': 'slot_name' if name in SLOT_NAMES else 'IsSlot=true',
                'field': 'Name'
            })

    return protected


if __name__ == '__main__':
    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('source/vanilla')
    protected = scan(source_dir)

    print(f"找到 {len(protected)} 個受保護的條目：")
    for p in protected:
        print(f"  Id={p['id']:>8}  Name={p['name']!r:<15}  原因: {p['reason']}")

    out_path = Path('glossary/protected.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(protected, f, ensure_ascii=False, indent=2)
    print(f"\n已寫入 {out_path}")
