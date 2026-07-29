# Writeup — endians (LACTF 2026, misc/easy)

## 辨識

`chall.txt` 打開是一串「怪字」：`氀愀挀琀昀笀㄀开猀甀爀㌀…`。注意這些字大多是「一個 ASCII 字母 + 一個 nul」湊成的寬字元。生成腳本 `gen.py`：

```python
text = "lactf{REDACTED}"
endian = text.encode(encoding="???").decode(encoding="???")  # 兩個 ??? 是不匹配的 UTF-16 BE/LE
open("chall.txt","wb").write(endian.encode())
```

亦即 ASCII flag 先以某一端序的 UTF-16 編碼，再以相反端序解碼，使每兩個位元組（例如 `00 6c`）被重新解讀成單一寬字元，於是 `l a c t f {` 變成 `氀 愀 挀 琀 昀 笀`。

## 解法

反向操作：把 `chall.txt` 讀入解成字串，再以 `UTF-16BE` 編碼、`UTF-16LE` 解碼（把端序換回來）。因為字串裡穿插的 nul 位元組在 UTF-8 解碼時會被丟棄，直接 `decode()` 也可行。

```python
chall = open("chall.txt", "rb").read()
print(chall.decode().encode(encoding="UTF-16BE").decode(encoding="UTF-16LE"))
```

輸出即為 ASCII flag。

## Flag

`lactf{1_sur3_h0pe_th1s_d0es_n0t_g3t_l0st_1n_translati0n!}`
