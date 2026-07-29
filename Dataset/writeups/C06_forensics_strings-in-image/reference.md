# Writeup — Glory of the Garden (picoCTF, forensics/easy)

## 辨識

題目給一張 JPEG（`garden.jpg`），提示「比看起來的多」，是典型「檔案尾端 / 未使用區段藏字串」的取證題。JPEG 影像資料結束後仍可附加任意位元組，這些附加內容不影響顯示，但會殘留在檔案裡。

## 解法

用 `strings` 把檔案中可列印的字元序列全部印出，再以 flag 前綴 `pico` 過濾即可命中：

```bash
strings garden.jpg | grep -i pico
```

輸出：

```text
Here is a flag "picoCTF{more_than_m33ts_the_3y3657BaB2C}"
```

flag 就是那段以純文字附加在影像資料之後的字串，`strings` 無需任何解碼即可讀出。

## Flag

`picoCTF{more_than_m33ts_the_3y3657BaB2C}`
