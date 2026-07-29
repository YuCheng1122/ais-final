# Writeup — Missing Bits (GlacierCTF 2023, crypto/medium)

## 辨識

`priv.key` 的最後一行是 `-----END RSA PRIVATE KEY-----`，開頭幾行是空白（被刪掉）。這是 PKCS#1 的 RSA 私鑰 PEM 格式：去掉 `-----` 邊界後，每行都是 base64，串起來就是一段 DER，內容依序為 `version, n, e, d, p, q, dP, dQ, qInv` 等整數。缺的正是最前面的 n（模數）那幾行。

## 把 PEM 還原成 DER hex

跳過 `-----` 邊界行，對其餘每行 base64 解碼再轉 hex，缺行以問號佔位（`pem2hex.py` / `decode_file.py` 的作法）：

```python
for line in filecontent_lines:
    if line.startswith("-----"):
        continue
    if line.strip() == "":
        print("?" * 96)
    else:
        decoded_lines += base64.b64decode(line).hex()
```

## 解析 DER 整數

DER 裡整數以 `02` 開頭，後接長度（長度 ≥ 0x80 時，`82` 表示「接下來 2 個位元組是長度」）。在還原出的 hex 中依序找 `02` 標頭：

- `0203010001`：長度 3，值 `0x010001` → 公開指數 e = 65537
- `02820100`：長度 `0x100`（256 bytes）→ 私鑰指數 **d**
- `028181`：長度 `0x81`（129 bytes）→ 質因數 **p**
- 再一個 `028181`：長度 `0x81` → 質因數 **q**

d、p、q 的位元組都完整保留，直接讀出即可：

```text
d = 0x0a9a25ba23342c18ab29...ae45033450becb5105416981
p = 0x00e4188b37b163c203ae...340bcb32a21
q = 0x00f122e285b030a36974...facafcd8569e7
```

## 重建模數並解密

缺的 n 用 `N = p * q` 直接補回，再以私鑰指數解密 `ciphertext_message`：

```python
from Crypto.Util.number import bytes_to_long, long_to_bytes
ct = open("ciphertext_message", "rb").read()
pt = pow(bytes_to_long(ct), d, p * q)
print(long_to_bytes(pt))
```

輸出：`Hey Bob this is Alice.\nI want to let you know that the Flag is gctf{7hi5_k3y_can_b3_r3c0ns7ruc7ed}`。

## Flag

`gctf{7hi5_k3y_can_b3_r3c0ns7ruc7ed}`
