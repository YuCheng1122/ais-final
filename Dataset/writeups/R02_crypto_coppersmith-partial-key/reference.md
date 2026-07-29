# Writeup — six-seven-again (LACTF 2026, crypto/medium)

## 辨識

`chall.py` 的 `generate_super_67_prime()` 產生一個 201 位十進位質數 `p`，數字結構固定為：最高 67 位全為 `6`、中間 67 位每位從 `{6,7}` 隨機、最低 67 位全為 `7`。另一質數 `q = getPrime(670)` 為普通 670 位元質數。`n = p*q`、`e = 65537`。

關鍵在於 `p` 幾乎完全已知：高 67 位與低 67 位完全固定，只有中間 67 位（一個 `[0,10^67)` 的整數 `x`）未知。可寫成

```
p = A + x * 10^67 ,  其中  A = int("6"*67 + "0"*67 + "7"*67)
```

未知量 `x` 相對於 `p` 很小，正是 Coppersmith 部分已知位元分解（partial known-bits factoring）的標準情境。

## 攻擊原理（SageMath）

在 `Zmod(n)[x]` 中定義 `f = A + x*10^67`，`p` 是它的一個根，且 `p | n`。將 `f` 化為 monic 後用 `small_roots` 求小根：

```python
R.<x> = PolynomialRing(Zmod(n))
A = Integer("6" * 67 + "0"*67 + "7"*67)
f = A + x*10^67
f_monic = f / f.leading_coefficient()
roots = f_monic.small_roots(X=10^68, beta=0.3)   # X 為未知量上界，beta ~ p 佔 n 的比例
p = int(roots[0]*10^67 + A)
q = n / p
```

`beta=0.3` 反映 `p`（約 668 位元）約佔 `n`（1337 位元）的一半以下；`X=10^68` 為中間未知塊的上界。求得中間塊後回填得到 `p`，再 `q = n / p`。

## RSA 解密

```python
t = (p-1)*(q-1)
d = pow(65537, -1, t)
m = pow(c, d, n)
print(long_to_bytes(m))
```

flag 中的 `667+670=1337` 也點出設計：`p` 約 668 位元、`q` 為 670 位元，`n` 約 1337 位元。

## Flag

`lactf{n_h4s_1337_b1ts_b3c4us3_667+670=1337}`
