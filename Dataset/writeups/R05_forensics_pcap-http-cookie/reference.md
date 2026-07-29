# Writeup — There will be cake (BYUCTF 2026, forensics/easy)

## 辨識

題目描述談的是「活動會被記錄、儲存」，且提示指向「幾乎每個網站都有、類似蛋糕的烘焙點心」——也就是 **cookie**。整個 pcap 裡唯一像 API 請求的封包就是 HTTP 請求／回應，所以從 HTTP 流量下手。

先過濾到 HTTP：

```bash
tshark -r GLaDOS_Network.pcapng -Y http
```

會看到一筆對某個 vibe-coded API 的請求（實際上是 POST）。

## 解法

檢視該請求的 `Cookie:` 標頭，會發現一個名為 `cake` 的 cookie，值是一串明顯的 base64：

```bash
tshark -r GLaDOS_Network.pcapng -Y 'http.cookie' -T fields -e http.cookie
# 或者最省事：
strings GLaDOS_Network.pcapng | grep -i cake
```

得到：

```text
Cookie: cake=Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ==
```

把 cookie 值 base64 解碼即為 flag：

```bash
echo -n 'Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ==' | base64 -d
```

## Flag

`byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}`
