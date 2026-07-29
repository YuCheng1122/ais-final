# Writeup — error-correction (LACTF 2026, misc/medium)

## 辨識

`chall.png` 是一張 450×450 的圖，明顯是一個被打亂的 QR code。生成腳本 `chall.py` 完整揭露了流程：

```python
qr = segno.make(flag, mode='byte', error='L', boost_error=False, version=7)
```

version 7 的 QR 為 45×45 模組，EC level 為 L（最低）。腳本把 45×45 模組陣列切成 **5×5 個 9×9 模組的區塊**（共 25 塊），索引方式為

```python
chunks[...] = code[405*y + 45*ysub + 9*x : 405*y + 45*ysub + 9*(x+1)]  # x,y in range(5), ysub in range(9)
```

然後 `random.shuffle(chunks)` 把 25 塊隨機重排，重新拼回並以 NEAREST 放大成 450×450 存成 `chall.png`（每個模組 = 10px）。

## 解法

1. 讀入 `chall.png`，以每 10px 一個模組降採樣回 45×45 的 0/1 模組陣列，再切回 25 個 9×9 區塊。
2. 這 25 塊是原 QR 5×5 佈局的一個排列。求正確排列的兩條路線：
   - **結構還原**：利用 QR 的三個角落定位圖案（finder patterns）、timing pattern 與 format info 判定每個區塊該在的位置，把 5×5 拼回；或
   - **暴搜 / 糾錯**：嘗試區塊排列並交給有糾錯能力的 QR 解碼器，找出能成功解出的排列。因為 `error='L'` 加上 flag 尾端刻意加上的 padding 後綴，QR 糾錯足以在區塊歸位後成功讀出。
3. 重組出的 version 7、byte mode、EC level L 的 QR 解碼後即得 flag。flag 尾端的 `CVOD5Jp7IOq+XgR` 是為了在打亂後仍保留足夠冗餘而附加的 padding，屬於 flag 的一部分。

## Flag

`lactf{Th15_15_pr0b481y_n07_wh47_7h3y_m34n7_8y_3rr0r_c0rr3c710n_CVOD5Jp7IOq+XgR}`
