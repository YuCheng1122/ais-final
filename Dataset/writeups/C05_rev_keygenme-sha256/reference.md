# Writeup — keygenme (picoCTF, rev/medium)

## 辨識

`keygenme-trial.py` 是「Arcane Calculator」試用版。選單 (c) `enter_license()` 會呼叫
`check_key(user_key, bUsername_trial)`，`bUsername_trial = b"FRASER"`。金鑰模板為：

```python
key_part_static1_trial = "picoCTF{1n_7h3_|<3y_of_"
key_part_dynamic1_trial = "xxxxxxxx"   # 8 碼動態
key_part_static2_trial  = "}"
```

即合法金鑰 = `picoCTF{1n_7h3_|<3y_of_` + 8 碼動態 + `}`，與 flag 同形。

## 金鑰推導邏輯

`check_key()` 先確認長度相符、靜態前綴逐字元相符，接著逐一比對 8 個動態字元。
關鍵在於這 8 碼是取 `sha256(b"FRASER").hexdigest()` 的特定索引，**且順序被打亂**：

```python
key[i+0] == sha256(username).hexdigest()[4]
key[i+1] == sha256(username).hexdigest()[5]
key[i+2] == sha256(username).hexdigest()[3]
key[i+3] == sha256(username).hexdigest()[6]
key[i+4] == sha256(username).hexdigest()[2]
key[i+5] == sha256(username).hexdigest()[7]
key[i+6] == sha256(username).hexdigest()[1]
key[i+7] == sha256(username).hexdigest()[8]
```

即動態部分 = hexdigest 索引序列 `[4, 5, 3, 6, 2, 7, 1, 8]` 依序取出的字元。

## 解法

在本機重算雜湊並依該索引順序取字元：

```python
import hashlib
h = hashlib.sha256(b"FRASER").hexdigest()
# h = 92d7ac3c9a0cf9d527a5906540d6c59c80bf8d7ad5bb1885f5f79b5b24a6d387
dynamic = "".join(h[i] for i in [4, 5, 3, 6, 2, 7, 1, 8])
print("picoCTF{1n_7h3_|<3y_of_" + dynamic + "}")
```

`sha256("FRASER")` 完整值為 `92d7ac3c9a0cf9d527a5906540d6c59c80bf8d7ad5bb1885f5f79b5b24a6d387`，
依索引 `[4,5,3,6,2,7,1,8]` 取出 `a, c, 7, 3, d, c, 2, 9` → 動態 8 碼 `ac73dc29`，組回即得 flag。

## Flag

`picoCTF{1n_7h3_|<3y_of_ac73dc29}`
