# Sunless Sea 存檔修改指南

## 存檔位置

```
~/Library/Application Support/unity.Failbetter Games.Sunless Sea/saves/
```

每個角色有兩個檔案：
- `{角色名}.json`：主存檔
- `{角色名}_fallback.json`：備援（遊戲讀取失敗時使用）

`Autosave.json` / `Autosave_fallback.json` 是獨立的自動存檔，**不是**角色存檔。修改時要確認角色名稱對應的檔案。

## 修改 Echo（金錢）

Echo 對應 `QualitiesPossessedList` 裡 `AssociatedQualityId = 102028` 的 `Level` 欄位。

```python
import json

name = "Charles"  # 替換成你的角色名
base = "/Users/chenyucheng/Library/Application Support/unity.Failbetter Games.Sunless Sea/saves"


for suffix in ["", "_fallback"]:
    path = f"{base}/{name}{suffix}.json"
    with open(path) as f:
        save = json.load(f)
    for q in save.get("QualitiesPossessedList", []):
        if q.get("AssociatedQualityId") == 102028:
            q["Level"] = 7000  # 目標金額
            break
    with open(path, "w") as f:
        json.dump(save, f, ensure_ascii=False)
    print(f"{path} 已更新")
```

## 注意事項

- **修改前必須關閉遊戲**，否則遊戲會用記憶體的舊值覆蓋回去
- 主存檔和 fallback 都要改，避免遊戲載入 fallback 時還原
- `Dosh` 欄位（頂層）目前確認值為 0，不影響顯示，實際 Echo 數值在 QualitiesPossessedList

## 其他已知 Quality ID

| Quality | Id |
|---------|-----|
| Echo（金錢） | 102028 |
