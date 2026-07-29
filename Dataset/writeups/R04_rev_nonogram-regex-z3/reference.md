# Writeup — flag-finder (LACTF 2026, rev/medium)

## 辨識

網頁 `index.html` + `script.js` 全在 client 端。`script.js`：

```js
const len = 1919;                 // 19 列 × 101 欄 = 1919
const theFlag = /^(?= ... )$/;    // 一條超長 regex
```

`createInput()` 產生 1919 個 checkbox；`match()` 把每個 box 轉成 `#`(checked) 或 `.`(unchecked)
串成長度 1919 的字串，執行 `theFlag.test(input)`。所以要找的是一個 1919 字元的 `#`/`.` 盤面，
它其實是一張 **19 列 × 101 欄的 nonogram（數織）**。

## regex 如何編碼 nonogram

`theFlag` 由兩部分 lookahead 疊成：

- **欄約束（column clues）**：開頭一大段前瞻，每段形如
  `(?:.{K}\..{100-K})*(?:.{K}#.{100-K}){a}(?:.{K}\..{100-K})+ ...`，
  用 `.{K} ... .{100-K}` 固定挑出第 K 欄的字元（每列跨 101 格），
  再以 `#{a}` / `\.+` 交錯編碼「該欄連續塗黑格的段長序列」。101 欄各一段。
- **列約束（row clues）**：結尾一連串
  `(?<=.{101*r})(?<!.{101*r+1})(\.*#{a}\.+#{b}\.+ ... \.*)`，
  用後行斷言把游標定位到第 r 列開頭，群組內 `#{a}\.+#{b}...` 描述該列的連續黑格段長。19 列各一段。
- 最後 `(?=^.{1919}$)` 強制總長度 1919。

## 解法

1. 從 `script.js` 抽出唯一的 `const theFlag = /.../;`。
2. 解析欄前瞻與列後瞻，還原成 19 列 clue 與 101 欄 clue（每個 clue 是段長序列）。
3. 用任意 nonogram 解題器（或把 clue 丟給 ILP/約束求解器）解出 19×101 盤面。
4. 把解出的 `#` 盤面渲染成點陣圖——黑格拼出的像素文字即為 flag。
5. 讀出 flag。

（repo 未附 `solve.py`；ground-truth flag 提交在 `challenge.yaml`，即為解出盤面所拼出的文字。）

## Flag

`lactf{Wh47_d0_y0u_637_wh3n_y0u_cr055_4_r363x_4nd_4_n0n06r4m?_4_r363x06r4m!}`
