# Writeup — Sequential LCG (GlacierCTF 2023, crypto/medium)

## 加密機制

`encrypt.py` 的 `Encryptor` 持有兩台隨機參數的線性同餘產生器 `self.lcgs = (LCG0, LCG1)`。加密時，每個字元取 7 個位元（`f"{ascii_char:07b}"`），對每個 bit 執行 `result.append(next(self.lcgs[bit]))`：

- bit = 0 → 取 **LCG0** 的下一個輸出
- bit = 1 → 取 **LCG1** 的下一個輸出

因此 `ct` 是「兩台 LCG 交錯輸出」的序列，光看數值分不出來自哪台。每加密完一個字元，兩台 LCG 各用自身接下來的四個輸出重新播種：

```python
self.lcgs = (
    LCG(next(lcgs[0]), next(lcgs[0]), next(lcgs[0]), next(lcgs[0])),
    LCG(next(lcgs[1]), next(lcgs[1]), next(lcgs[1]), next(lcgs[1])),
)
```

## 切入點：首字為 `g`

flag 前綴固定為 `gctf{...}`，首字 `g` = `0x67` = `1100111`。所以第一個字元的 7 個位元中，bit=1 的位置是 index 0,1,4,5,6，這些位置的密文正是 **LCG1 的連續輸出**：

```python
known_consecutive_values = [RESULTS[0], RESULTS[1], RESULTS[4], RESULTS[5], RESULTS[6]]
```

## 從連續輸出還原 LCG 參數

對連續輸出 x0..x4，令 delta d_i = x_{i+1} - x_i。有恆等式 `d_{i} * d_{i+2} - d_{i+1}^2 ≡ 0 (mod n)`，因此取多組 `d1*d3 - d2**2` 的最大公因數即得模數 n：

```python
n_times_k = [d1*d3 - d2**2 for d1,d2,d3 in zip(deltas, deltas[1:], deltas[2:])]
mod = gcd(n_times_k[0], n_times_k[1])
```

有了 n，乘數 a 與增量 c 直接解：

```python
mult = ((x2 - x3) * inverse((x1 - x2), mod)) % mod      # calc_multiplicator
add  = (x2 - x1 * mult) % mod                            # calc_summand
```

## 回放區分每個位元

用還原出的 LCG1（mod, mult, add）逐位元重放整段 `ct`。第一個位元已知是 1，把 LCG1 的 seed 設為該密文值。之後每個位元：先算 LCG1 應該輸出的下一個值 `rng_next_val`，若與密文相符 → 該位元是 1（來自 LCG1）；若不符 → 該位元是 0（來自 LCG0），並把 LCG1 的內部 value 還原回上一個 seed，避免與加密端失步：

```python
seed = lcg.value
rng_next_val = next(lcg)
if rng_next_val == encrypted_bit:
    flag_bits.append(1)
else:
    flag_bits.append(0)
    lcg.value = seed
```

每處理完一個字元（7 bit），同樣用 `LCG(next(lcg), next(lcg), next(lcg), next(lcg))` 重新播種 LCG1，跟上加密端的節奏。最後把位元每 7 個一組還原成字元即得 flag。

## Flag

`gctf{th15_lcg_3ncryp710n_w4sn7_s0_5s3cur3_aft3r_4ll}`
