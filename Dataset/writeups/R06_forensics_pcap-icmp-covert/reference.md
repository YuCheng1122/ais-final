# Writeup — Are You Still There? (BYUCTF 2026, forensics/medium)

## 辨識

標題「Are you still there?」與附上的《Still Alive》歌詞（不斷重複 "still alive"）本身不直接給答案，但暗示要找「反覆確認某物是否還活著／還在線上」的封包。提示更直白：「你會怎麼遠端檢查一台伺服器是否還在線上？」——答案就是 **ping**，也就是 **ICMP echo request** 封包。

過濾到 ICMP echo request：

```bash
tshark -r GLaDOS_Network.pcapng -Y 'icmp.type == 8'
```

## 觀察

逐一檢視這些 ping 封包的 payload 尾端，會發現第一個封包尾端是 ASCII `byuc`，下一個是 `tf{T`，再下一個是 `urr3`……幾乎每個 echo request 的 payload 都攜帶 4 個 ASCII 字元。這代表 flag 被拆開、依序分散在多個 ICMP 封包中傳送（ICMP 隱蔽通道）。

## 解法

有兩種做法：手動把每個封包尾端的字元抄下來拼起來，或寫腳本自動化。依 ICMP **sequence number** 排序後串接各封包 payload 即可。committed 解法（`pingDataSolver.py`）自行解析 pcapng 的 Enhanced Packet Block、抽出 IP→ICMP（proto 1、type 8）的 payload，用序號當 key 蒐集後排序串接：

```python
import struct

data = open("GLaDOS_Network.pcapng", "rb").read()
packets, off = [], 0
while off < len(data):
    if off + 8 > len(data): break
    btype = struct.unpack_from('<I', data, off)[0]
    blen  = struct.unpack_from('<I', data, off + 4)[0]
    if blen == 0 or off + blen > len(data): break
    block = data[off:off + blen]
    if btype == 0x00000006:            # Enhanced Packet Block
        cap_len = struct.unpack_from('<I', block, 20)[0]
        packets.append(block[28:28 + cap_len])
    off += blen

chunks = {}
for pkt in packets:
    if len(pkt) < 14 or struct.unpack_from('>H', pkt, 12)[0] != 0x0800:
        continue                        # not IPv4
    ihl = (pkt[14] & 0x0F) * 4
    proto, payload = pkt[14 + 9], pkt[14 + ihl:]
    if proto != 1 or len(payload) < 8:  # ICMP
        continue
    if payload[0] != 8:                 # echo request only
        continue
    seq = struct.unpack_from('>I', payload, 4)[0]
    chunks[seq] = payload[8:]           # bytes after the 8-byte ICMP header

flag = b"".join(chunks[k] for k in sorted(chunks.keys()))
print(flag.rstrip(b'\x00').decode(errors='replace'))
```

共 12 個 echo request（seq 0..11），各帶 4 bytes，依序組出：`byuc` + `tf{T` + `urr3` + … → flag。用 scapy（`rdpcap` + `ICMP` layer，取 `pkt[ICMP].seq` 與 `bytes(pkt[Raw])`）同樣可做。

## Flag

`byuctf{Turr3t_R3d3mpt!0n_L!n3s_4r3_N0t_R!d3s}`
