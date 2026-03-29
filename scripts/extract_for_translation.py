#!/usr/bin/env python3
"""
從各 JSON 檔案抽出需要翻譯的欄位，存成精簡的 flat 格式。
目的：讓在對話中翻譯時不需要載入完整 JSON，節省 context。

輸出：source/en/flat/{category}/{file}_flat.json
"""
import json
import os
import sys

BASE_EN = "/Users/chenyucheng/projects/sunless-sea-zh-tw/source/en"
BASE_FLAT = "/Users/chenyucheng/projects/sunless-sea-zh-tw/source/en/flat"
PROTECTED_PATH = "/Users/chenyucheng/projects/sunless-sea-zh-tw/glossary/protected.json"


def load_protected():
    data = json.load(open(PROTECTED_PATH))
    return {item["id"] for item in data}


def extract_qualities(protected_ids):
    src = json.load(open(f"{BASE_EN}/entities/qualities.json"))
    result = []
    for item in src:
        if item["Id"] in protected_ids:
            continue
        entry = {"Id": item["Id"]}
        for field in ["Name", "Description", "ChangeDescriptionText", "LevelDescriptionText", "LevelImageText"]:
            if item.get(field):
                entry[field] = item[field]
        if len(entry) > 1:  # 有翻譯欄位
            result.append(entry)
    return result


def extract_events():
    src = json.load(open(f"{BASE_EN}/entities/events.json"))
    result = []
    for item in src:
        entry = {"Id": item["Id"]}
        for field in ["Name", "Description"]:
            if item.get(field):
                entry[field] = item[field]

        # 抽取 ChildBranches 中的文字欄位
        branches = []
        for branch in item.get("ChildBranches", []):
            b = {"Id": branch["Id"]}
            for field in ["Name", "Description", "ButtonText"]:
                if branch.get(field):
                    b[field] = branch[field]

            de = branch.get("DefaultEvent", {})
            if de:
                d = {"Id": de["Id"]}
                for field in ["Name", "Description"]:
                    if de.get(field):
                        d[field] = de[field]
                if len(d) > 1:
                    b["DefaultEvent"] = d

            if len(b) > 1:
                branches.append(b)

        if branches:
            entry["ChildBranches"] = branches

        if len(entry) > 1:
            result.append(entry)
    return result


def extract_exchanges():
    src = json.load(open(f"{BASE_EN}/entities/exchanges.json"))
    result = []
    for i, item in enumerate(src):
        entry = {"_index": i}
        for field in ["Name", "Title", "Description"]:
            if item.get(field):
                entry[field] = item[field]

        shops = []
        for shop in item.get("Shops", []):
            s = {}
            for field in ["Name", "Description"]:
                if shop.get(field):
                    s[field] = shop[field]
            if s:
                shops.append(s)
        if shops:
            entry["Shops"] = shops

        if len(entry) > 1:
            result.append(entry)
    return result


def extract_personas():
    src = json.load(open(f"{BASE_EN}/entities/personas.json"))
    result = []
    for item in src:
        entry = {}
        if item.get("Id"):
            entry["Id"] = item["Id"]
        for field in ["Name", "Description", "Title"]:
            if item.get(field):
                entry[field] = item[field]
        if len(entry) > 1:
            result.append(entry)
    return result


def extract_encyclopaedia():
    enc_dir = f"{BASE_EN}/encyclopaedia"
    results = {}
    for fname in sorted(os.listdir(enc_dir)):
        if not fname.endswith(".json"):
            continue
        src = json.load(open(f"{enc_dir}/{fname}"))
        file_result = []
        for item in src:
            entry = {}
            if item.get("Id"):
                entry["Id"] = item["Id"]
            for field in ["Name", "Description", "Title", "Teaser"]:
                if item.get(field):
                    entry[field] = item[field]
            if len(entry) > 1:
                file_result.append(entry)
        if file_result:
            results[fname] = file_result
    return results


def save(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  寫入 {path} ({len(data)} 條)")


def main():
    protected = load_protected()
    print(f"受保護 ID：{len(protected)} 條")

    print("\n抽取 qualities...")
    data = extract_qualities(protected)
    save(data, f"{BASE_FLAT}/entities/qualities_flat.json")

    print("\n抽取 events...")
    data = extract_events()
    save(data, f"{BASE_FLAT}/entities/events_flat.json")

    print("\n抽取 exchanges...")
    data = extract_exchanges()
    save(data, f"{BASE_FLAT}/entities/exchanges_flat.json")

    print("\n抽取 personas...")
    data = extract_personas()
    save(data, f"{BASE_FLAT}/entities/personas_flat.json")

    print("\n抽取 encyclopaedia...")
    results = extract_encyclopaedia()
    for fname, file_data in results.items():
        save(file_data, f"{BASE_FLAT}/encyclopaedia/{fname.replace('.json', '_flat.json')}")

    print("\n完成！flat 檔案位於:", BASE_FLAT)


if __name__ == "__main__":
    main()
