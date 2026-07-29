# Writeup — hash sling / level5 (picoCTF, misc/medium)

## 辨識

`level5.py` 的驗證邏輯：讀入密文 `level5.flag.txt.enc` 與正確密碼雜湊 `level5.hash.bin`，
把使用者輸入的密碼取 `hashlib.md5(...).digest()` 後與 `correct_pw_hash` 比對；相符才用
`str_xor(flag_enc.decode(), user_pw)` 把 flag 解出來（以密碼字串循環延展後逐位元 XOR）。

原始程式只等使用者手動輸入單一密碼，並無爆破。關鍵是把候選密碼來源換成 `dictionary.txt`，
逐一嘗試直到 MD5 命中 `level5.hash.bin`。

## 解法

以字典檔逐行爆破，命中即用該密碼 XOR 解出 flag：

```python
import hashlib

def str_xor(secret, key):
    new_key = key
    i = 0
    while len(new_key) < len(secret):
        new_key = new_key + key[i]
        i = (i + 1) % len(key)
    return "".join(chr(ord(s) ^ ord(k)) for s, k in zip(secret, new_key))

flag_enc = open('level5.flag.txt.enc', 'rb').read()
correct_pw_hash = open('level5.hash.bin', 'rb').read()   # e8352e76e260a31eb266012f70df9a10

for pw in open('dictionary.txt').read().splitlines():
    if hashlib.md5(pw.encode()).digest() == correct_pw_hash:
        print(pw, '->', str_xor(flag_enc.decode(), pw))
        break
```

字典中命中的密碼為 `7e5f`（其 MD5 為 `e8352e76e260a31eb266012f70df9a10`，與 `level5.hash.bin` 相符），
用它對 `level5.flag.txt.enc` 做 `str_xor` 即還原出 flag。

## Flag

`picoCTF{h45h_sl1ng1ng_40f26f81}`
