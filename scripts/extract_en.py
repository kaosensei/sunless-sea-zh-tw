#!/usr/bin/env python3
"""
extract_en.py - 從 Sunless.Game.dll 提取英文原文 JSON 到 source/en/

用法：
    python3 scripts/extract_en.py

輸出到 source/en/，目錄結構與 source/vanilla/ 相同。
"""

import json
import os
import sys

DLL_PATH = os.path.expanduser(
    "~/Library/Application Support/Steam/steamapps/common/"
    "SunlessSea/Sunless Sea.app/Contents/Resources/Data/Managed/Sunless.Game.dll"
)
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "source", "en")

BOM = b"\xef\xbb\xbf"

# -------------------------------------------------------------------
# 從 DLL raw bytes 找所有 BOM+[ 的起點
# -------------------------------------------------------------------

def find_bom_starts(raw, search_start=900_000, search_end=5_100_000):
    starts = []
    idx = raw.find(BOM, search_start)
    while 0 < idx < search_end:
        starts.append(idx)
        idx = raw.find(BOM, idx + 1)
    return starts


def parse_json_block(raw, start, next_start):
    """
    從 start 到 next_start 之間，找最後一個 ']' 作為 JSON 結尾並解析。
    回傳 (data, actual_end) 或 (None, 0)。
    """
    window = raw[start:next_start]
    last_bracket = window.rfind(b"]")
    if last_bracket < 0:
        return None, 0
    end = start + last_bracket + 1
    text = raw[start:end].decode("utf-8-sig", errors="replace")
    try:
        return json.loads(text), end
    except json.JSONDecodeError as e:
        return None, 0


# -------------------------------------------------------------------
# 主流程
# -------------------------------------------------------------------

def main():
    if not os.path.exists(DLL_PATH):
        print(f"ERROR: DLL 不存在：{DLL_PATH}")
        sys.exit(1)

    print(f"讀取 DLL：{DLL_PATH}")
    with open(DLL_PATH, "rb") as f:
        raw = f.read()
    print(f"DLL 大小：{len(raw):,} bytes\n")

    starts = find_bom_starts(raw)
    print(f"找到 {len(starts)} 個 BOM 標記\n")

    # 根據 first entry 辨識各 block
    block_map = identify_blocks(raw, starts)

    # 輸出目錄
    os.makedirs(OUT_DIR, exist_ok=True)
    for subdir in ["entities", "encyclopaedia", "geography"]:
        os.makedirs(os.path.join(OUT_DIR, subdir), exist_ok=True)

    # 寫出
    total = 0
    for rel_path, data in sorted(block_map.items()):
        out_path = os.path.join(OUT_DIR, rel_path)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  ✅  {rel_path} ({len(data)} 條)")
        total += len(data)

    print(f"\n共提取 {total} 條英文原文，輸出至 {OUT_DIR}/")


def identify_blocks(raw, starts):
    """
    解析每個 block，根據第一個 entry 的欄位判斷是哪個 JSON 檔案。
    回傳 { rel_path: [list of entries] }
    """
    result = {}
    parsed = []

    for i, start in enumerate(starts):
        next_start = starts[i + 1] if i + 1 < len(starts) else start + 10_000_000
        data, end = parse_json_block(raw, start, next_start)
        if data is None or not isinstance(data, list) or len(data) == 0:
            continue
        first = data[0]
        parsed.append((start, data, first))

    for start, data, first in parsed:
        keys = set(first.keys())
        count = len(data)

        # areas.json: Name + Description + ImageName + Id (DLL 版沒有 MapX)
        if "ImageName" in keys and "Name" in keys and "Id" in keys \
                and "ChildBranches" not in keys and "Shops" not in keys \
                and count < 200:
            result["entities/areas.json"] = data

        # events.json: ChildBranches 是獨有欄位
        elif "ChildBranches" in keys and count > 100:
            result["entities/events.json"] = data

        # qualities.json: PyramidNumberIncreaseLimit 是獨有欄位
        elif "PyramidNumberIncreaseLimit" in keys and count > 100:
            result["entities/qualities.json"] = data

        # personas.json: QualitiesAffected + QualitiesRequired + Setting
        elif "QualitiesAffected" in keys and "QualitiesRequired" in keys and "Setting" in keys:
            result["entities/personas.json"] = data

        # exchanges.json: Shops 是獨有欄位
        elif "Shops" in keys:
            result["entities/exchanges.json"] = data

        # Tutorials.json: ShouldPause 是獨有欄位
        elif "ShouldPause" in keys:
            result["encyclopaedia/Tutorials.json"] = data

        # CombatAttacks.json: QualityRequired + Image
        elif "QualityRequired" in keys and "Image" in keys and count > 20:
            result["encyclopaedia/CombatAttacks.json"] = data

        # CombatItems.json: AssociatedQualityId 是獨有欄位
        elif "AssociatedQualityId" in keys:
            result["encyclopaedia/CombatItems.json"] = data

        # SpawnedEntities.json: HumanName + PrefabName + BehaviourName
        elif "HumanName" in keys and "PrefabName" in keys and "BehaviourName" in keys:
            result["encyclopaedia/SpawnedEntities.json"] = data

        # TileSets.json: MapWidth + MapHeight
        elif "MapWidth" in keys:
            result["geography/TileSets.json"] = data

        # TileRules.json: TileNames
        elif "TileNames" in keys:
            result["geography/TileRules.json"] = data

    return result


if __name__ == "__main__":
    main()
