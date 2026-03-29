# Sunless Sea 繁體中文漢化

Sunless Sea 非官方繁體中文（台灣）翻譯 mod。

從英文原文直接翻譯，以維多利亞哥德 × 克蘇魯宇宙恐怖的文風，重建原作的氛圍與節奏。

**遊戲版本**：Steam v2.2.11.3212（含 Zubmariner DLC）

---

## 翻譯範圍

| 類別 | 筆數 | 說明 |
|------|------|------|
| 物品 / 故事旗標（Qualities） | 953 | 含屬性、物品、進度標記 |
| 事件 / 卡片（Events） | 872 | 主線、支線、隨機事件 |
| 商店（Exchanges） | 31 | 含 Zubmariner DLC 水下港口 |
| 教學（Tutorials） | 34 | 含 Zubmariner DLC 潛航教學 |
| 地圖磁磚（Tiles） | 36 | 港口、地點顯示名稱 |

---

## 安裝方式

### macOS

將 `addon/vanilla/` 整個資料夾複製到：

```
~/Library/Application Support/unity.Failbetter Games.Sunless Sea/addon/sunless-sea-zh-tw/
```

完成後目錄結構應如下：

```
addon/
  sunless-sea-zh-tw/
    entities/
      events.json
      qualities.json
      exchanges.json
    encyclopaedia/
      Tutorials.json
    geography/
      Tiles.json
```

### Windows

將 `addon/vanilla/` 複製到：

```
%USERPROFILE%\AppData\LocalLow\Failbetter Games\Sunless Sea\addon\sunless-sea-zh-tw\
```

### 啟動遊戲

複製完成後直接啟動遊戲，遊戲會自動讀取 addon 目錄下的翻譯。無需任何額外設定。

---

## 備注

- 部分 NPC 稱呼玩家的通知訊息（「你的 X 屬性提升了」）為遊戲引擎硬編碼，無法透過 addon 替換，會以英文顯示。
- Personas（船員戰鬥識別碼）為技術性字串，無玩家可見文字，未翻譯。

---

## 致謝

[InstantComet/SunlessSea](https://github.com/InstantComet/SunlessSea) 簡體中文譯本的譯者在 `events.json` 中留下的翻譯，是本專案制定風格指南時的重要參考——從中歸納出克蘇魯文體的中文處理方式，以及術語譯名的選擇方向。在此致謝。

---

## 版權聲明

All game content belongs to Failbetter Games. This is a non-commercial fan translation project.

本翻譯從英文原文獨立翻譯，文字內容與簡體中文譯本無直接從屬關係。
