#!/usr/bin/env python3
"""
把翻譯好的 flat 檔案合回 addon 格式，輸出至 translations/vanilla/。

用法：
  python3 merge_translations.py qualities     # 合併 qualities
  python3 merge_translations.py events        # 合併 events
  python3 merge_translations.py exchanges     # 合併 exchanges
  python3 merge_translations.py personas      # 合併 personas
  python3 merge_translations.py all           # 合併全部
  python3 merge_translations.py status        # 顯示翻譯進度

翻譯輸入：source/en/flat/{category}/{file}_translated.json
輸出：translations/vanilla/{category}/{file}.json
"""
import json
import os
import sys

BASE_FLAT = "/Users/chenyucheng/projects/sunless-sea-zh-tw/source/en/flat"
BASE_TRANS = "/Users/chenyucheng/projects/sunless-sea-zh-tw/translations/vanilla"


def load_json(path):
    if not os.path.exists(path):
        return None
    return json.load(open(path, encoding="utf-8"))


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_status():
    """顯示各檔案翻譯進度。"""
    files = [
        ("entities/qualities_flat.json", "entities/qualities_translated.json"),
        ("entities/events_flat.json", "entities/events_translated.json"),
        ("entities/exchanges_flat.json", "entities/exchanges_translated.json"),
        ("entities/personas_flat.json", "entities/personas_translated.json"),
    ]
    print(f"\n{'檔案':<35} {'英文原文':>8} {'已翻譯':>8} {'進度':>8}")
    print("-" * 65)
    for flat_rel, trans_rel in files:
        flat = load_json(f"{BASE_FLAT}/{flat_rel}")
        trans = load_json(f"{BASE_FLAT}/{trans_rel}")
        total = len(flat) if flat else 0
        done = len(trans) if trans else 0
        pct = f"{done/total*100:.0f}%" if total > 0 else "—"
        print(f"{flat_rel:<35} {total:>8} {done:>8} {pct:>8}")


def merge_qualities():
    trans_path = f"{BASE_FLAT}/entities/qualities_translated.json"
    src_path = "/Users/chenyucheng/Library/Application Support/unity.Failbetter Games.Sunless Sea/entities/qualities.json"
    trans = load_json(trans_path)
    src = load_json(src_path)
    if not trans:
        print("找不到翻譯檔：", trans_path)
        return
    if not src:
        print("找不到原始檔：", src_path)
        return

    import copy
    src_by_id = {item["Id"]: item for item in src}
    out_path = f"{BASE_TRANS}/entities/qualities.json"
    result = []
    for item in trans:
        qid = item["Id"]
        if qid not in src_by_id:
            print(f"  警告：找不到 Id={qid} 的原始資料，跳過")
            continue
        entry = copy.deepcopy(src_by_id[qid])
        for field in ["Name", "Description", "ChangeDescriptionText", "LevelDescriptionText", "LevelImageText"]:
            if item.get(field):
                entry[field] = item[field]
        result.append(entry)

    save_json(result, out_path)
    print(f"qualities 合併完成：{len(result)} 條 → {out_path}")


def merge_events():
    trans_path = f"{BASE_FLAT}/entities/events_translated.json"
    src_path = "/Users/chenyucheng/Library/Application Support/unity.Failbetter Games.Sunless Sea/entities/events.json"
    trans = load_json(trans_path)
    src = load_json(src_path)
    if not trans:
        print("找不到翻譯檔：", trans_path)
        return

    import copy
    # 以完整原始資料為底，只替換文字欄位
    src_by_id = {item["Id"]: item for item in src}
    result = []
    for t in trans:
        eid = t["Id"]
        if eid not in src_by_id:
            print(f"  警告：找不到 Id={eid} 的原始資料，跳過")
            continue
        entry = copy.deepcopy(src_by_id[eid])
        for field in ["Name", "Description"]:
            if t.get(field):
                entry[field] = t[field]
        # 替換 ChildBranches 文字
        trans_branches = {b["Id"]: b for b in t.get("ChildBranches", [])}
        for branch in entry.get("ChildBranches", []):
            tb = trans_branches.get(branch["Id"])
            if not tb:
                continue
            for field in ["Name", "Description", "ButtonText"]:
                if tb.get(field):
                    branch[field] = tb[field]
            # 替換 DefaultEvent 文字
            tde = tb.get("DefaultEvent")
            if tde and branch.get("DefaultEvent"):
                for field in ["Name", "Description"]:
                    if tde.get(field):
                        branch["DefaultEvent"][field] = tde[field]
        result.append(entry)

    out_path = f"{BASE_TRANS}/entities/events.json"
    save_json(result, out_path)
    print(f"events 合併完成：{len(result)} 條 → {out_path}")


def merge_exchanges():
    trans_path = f"{BASE_FLAT}/entities/exchanges_translated.json"
    src_path = "/Users/chenyucheng/projects/sunless-sea-zh-tw/source/en/entities/exchanges.json"
    trans = load_json(trans_path)
    src = load_json(src_path)
    if not trans:
        print("找不到翻譯檔：", trans_path)
        return

    # 以完整原始資料為底，只替換文字欄位
    import copy
    result = copy.deepcopy(src)

    for item in trans:
        idx = item.get("_index")
        if idx is None or idx >= len(result):
            continue
        entry = result[idx]
        for field in ["Name", "Title", "Description"]:
            if item.get(field):
                entry[field] = item[field]
        # 替換 Shops 文字
        trans_shops = item.get("Shops", [])
        src_shops = entry.get("Shops", [])
        for i, ts in enumerate(trans_shops):
            if i < len(src_shops):
                for field in ["Name", "Description"]:
                    if ts.get(field):
                        src_shops[i][field] = ts[field]

    out_path = f"{BASE_TRANS}/entities/exchanges.json"
    save_json(result, out_path)
    print(f"exchanges 合併完成：{len(result)} 條 → {out_path}")


def merge_personas():
    trans_path = f"{BASE_FLAT}/entities/personas_translated.json"
    trans = load_json(trans_path)
    if not trans:
        print("找不到翻譯檔：", trans_path)
        return

    out_path = f"{BASE_TRANS}/entities/personas.json"
    result = []
    for item in trans:
        entry = {}
        if item.get("Id"):
            entry["Id"] = item["Id"]
        for field in ["Name", "Description", "Title"]:
            if item.get(field):
                entry[field] = item[field]
        result.append(entry)

    save_json(result, out_path)
    print(f"personas 合併完成：{len(result)} 條 → {out_path}")


def merge_tutorials():
    trans_path = f"{BASE_FLAT}/encyclopaedia/Tutorials_translated.json"
    src_path = "/Users/chenyucheng/projects/sunless-sea-zh-tw/source/en/encyclopaedia/Tutorials.json"
    trans = load_json(trans_path)
    src = load_json(src_path)
    if not trans:
        print("找不到翻譯檔：", trans_path)
        return

    import copy
    src_by_id = {item["Id"]: item for item in src}
    result = []
    for t in trans:
        tid = t["Id"]
        if tid not in src_by_id:
            print(f"  警告：找不到 Id={tid} 的原始資料，跳過")
            continue
        entry = copy.deepcopy(src_by_id[tid])
        for field in ["Name", "Description"]:
            if t.get(field):
                entry[field] = t[field]
        result.append(entry)

    out_path = f"{BASE_TRANS}/encyclopaedia/Tutorials.json"
    save_json(result, out_path)
    print(f"Tutorials 合併完成：{len(result)} 條 → {out_path}")


COMMANDS = {
    "qualities": merge_qualities,
    "events": merge_events,
    "exchanges": merge_exchanges,
    "personas": merge_personas,
    "tutorials": merge_tutorials,
    "status": show_status,
    "all": lambda: [f() for f in [merge_qualities, merge_events, merge_exchanges, merge_personas, merge_tutorials]],
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd not in COMMANDS:
        print(f"未知命令：{cmd}。可用：{', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[cmd]()
