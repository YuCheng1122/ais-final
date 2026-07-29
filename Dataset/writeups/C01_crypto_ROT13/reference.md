# Writeup — ROT13 (picoCTF, crypto/easy)

## 辨識

密文開頭是 `cvpbPGS{`。flag 前綴固定為 `picoCTF{`，把 `picoCTF` 每個字母往後移 13 位即得 `cvpbPGS`——這是 ROT13 的強辨識訊號（`p→c, i→v, c→p, o→b, C→P, T→G, F→S`）。

## 解法

對密文套 ROT13（A–Z、a–z 各 +13 mod 26，非字母保留）。ROT13 自逆，加解密同一運算。

```bash
echo 'cvpbPGS{abg_gbb_onq_bs_n_ceboyrz}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

或 Python：`codecs.decode(ciphertext, 'rot_13')`。

## Flag

`picoCTF{not_too_bad_of_a_problem}`
