# SUNLESS SEA 繁體中文漢化

<img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/29bc8b03-b153-488c-87b2-2848bd4b3417" />

SUNLESS SEA 非官方繁體中文翻譯 mod。

非常久以前就想玩《SUNLESS SEA（無光之海）》這款遊戲了，尤其讀完狐尾的《詭祕地海》後，更是想要親歷地海的詭異與瑰麗。這款遊戲在玩家社群裡素有「雅思之海」的戲稱，形容其艱澀的用詞及龐大的文本量如同語言測驗「雅思」的難度。

從前一直想著等自己英文足夠好再來玩，但想想「足夠好」的那天或許永遠不會來臨，趁著最近用 Claude Code 做了很多小玩具，乾脆就以「將遊戲文本中文化」作為目標練練手。

原本的目標只是將既有的[簡中翻譯](https://github.com/InstantComet/SunlessSea)轉成繁體版，再替換成臺灣的常用詞，但看了一輪簡中譯本後，對翻譯品質及譯筆實在不太滿意，決定試著直接用英文原文重新翻譯。

在生成式 AI 甚囂塵上的日子以前，我曾經簡單翻譯過幾篇英文文章，對於翻譯需要注意的事情有一些非常初步的概念，身為克系的愛好者，也還算分得出怎樣是「好的克蘇魯翻譯」，初步請 Claude 研究過[克系文學的特色](https://github.com/kaosensei/sunless-sea-zh-tw/blob/main/docs/%E5%85%8B%E8%98%87%E9%AD%AF%E7%BF%BB%E8%AD%AF%E7%A0%94%E7%A9%B6%E6%91%98%E8%A6%81.md)後，我就結合原本簡中譯者在 event.json 中留下的關鍵名詞及翻譯策略（例如「Fallen London」譯為「淪敦」這個巧思我就非常欣賞），制定了本次翻譯的[風格指南](https://github.com/kaosensei/sunless-sea-zh-tw/blob/main/docs/style-guide.md)，儘可能確保 AI 在大量翻譯時保持名詞和風格的一致性。

從結果而言，我得說翻譯的結果非常不錯！依據風格指南產出的結果完全符合我想要的風格。

翻譯完成後，我儘可能跑了多次檢核確保翻譯品質。不過因為這是我第一次使用 AI 處理這麼大量的文本，絕對會有不夠完善之處，若有注意到需要修正的地方，歡迎直接發 issue 提醒我，我會儘快修正。

**遊戲購買連結**：https://store.steampowered.com/app/304650/SUNLESS_SEA/

**遊戲版本**：Steam v2.2.11.3212（含 Zubmariner DLC）

這是我在 Steam 買的版本，他們上次更新在 2023 年 1 月了，未來我猜是不會再更新。

---

## 翻譯範圍

遊戲裡的文本包括人物、地點、物品、事件、教學等等基本上都翻譯了，不過你會注意到 UI 還是英文的，這是因為修改 UI 要用另一個方式（而且似乎很麻煩），所以不在本次處理的範圍。不過 UI 都是非常簡單的單字，看不懂的人稍微查個字典也可以玩了，真的想修改 UI 的人或許可以參考 [tinygrox 的專案](https://github.com/tinygrox/SunlessSeaCN)

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
      SpawnedEntities.json
      CombatItems.json
      CombatAttacks.json
    geography/
      Tiles.json
```

### Windows

將 `addon/vanilla/` 複製到：

```
%USERPROFILE%\AppData\LocalLow\Failbetter Games\Sunless Sea\addon\sunless-sea-zh-tw\
```

註：在我的 MacBook 上跑起來沒有問題，但我不確定 Windows 的路徑是否正確，如果有人遇到問題可以再跟我說。

### 啟動遊戲

複製完成後直接啟動遊戲，遊戲會自動讀取 addon 目錄下的翻譯。無需任何額外設定。

---

## 翻譯比較

我請 Claude 隨機抽樣了幾組原文跟翻譯來比對，說明我想要重原文直接翻譯的原因。

---

**案例一：語氣（Id 189552）**

> EN: Rain at funerals is decorous. The Neath chooses to grace this afternoon with one of its thin and melancholy showers.

> 繁中：葬禮上的雨是得體的。地底以其稀薄、憂鬱的細雨來恩賜這個下午。

> 簡中：细雨使得葬礼显得格外肃穆。

Claude：原文首句是一個近乎白描的陳述，語氣疏離冷靜。簡中加入「格外」，並改成因果句，把旁觀式敘事轉成了情緒鋪墊。Sunless Sea 最核心的文體特色——用平靜的口吻說可怕或哀傷的事——在這一句話裡消失了。

---

**案例二：誤譯（Id 144262）**

> EN: The silence will press on the ship with the weight of a cathedral, but we will forge on, East.

> 繁中：寂靜將以大教堂的重量壓在船上，但我們將繼續向東。

> 簡中：这寂静可以……推进这船，并且和东方结合起来。

Claude：「press on」（向下重壓）被譯成「推进」（向前推進），方向完全相反。原文是沉默如大教堂的重量令人喘不過氣，簡中版變成了「寂靜推動船前進」。「forge on, East」（奮力向東）也成了「和東方結合」，意義不明。

---

**案例三：語氣（Id 143367）**

> EN: An enormous crowned statue casts a chilling shadow.

> 繁中：一座巨大的加冕雕像投下令人不寒而慄的陰影。

> 簡中：一个巨大的……雕像投下了一片骇人的阴影。

Claude：「chilling」是冷靜的形容詞，語感近乎客觀描述。「骇人」帶有更激烈的驚嚇感，把沉著的旁觀者視角推向了戲劇化，原文那種維多利亞式的隱忍被打破。

---

## 致謝

[InstantComet/SunlessSea](https://github.com/InstantComet/SunlessSea) 簡中譯本的譯者在 `events.json` 中留下的翻譯，是我制定風格指南時的重要參考，在此致謝。

---

## 版權聲明

所有遊戲內容均屬於 Failbetter Games。本專案為非商業性的粉絲翻譯計畫。

All game content belongs to Failbetter Games. This is a non-commercial fan translation project.
