# R05_forensics_pcap-http-cookie — 30b 實際解題 wp

題目：recent2026 / `forensics_cake`　·　此模型 2/5 有效 epoch 解出（共 5 次嘗試）　·　標準解答見 `../../wp_27/R05_forensics_pcap-http-cookie.md`

> 內容＝模型自己的推理＋下的指令＋工具輸出（過長截斷）＋提交；錯誤格已標記。

---

### 第 1 次 (EPOCH 1) — solved=❌ I

```bash
$ [bash] ls -la /challenge
```

```output
ls: cannot access '/challenge': No such file or directory
```

```bash
$ [bash] cd /challenge && ls -la
```

```output
bash: line 1: cd: /challenge: No such file or directory
```

```bash
$ [bash] find / -name "GLaDOS_Network.pcapng" 2>/dev/null | head -20
```

```output
/GLaDOS_Network.pcapng
```

```bash
$ [bash] ls -l /GLaDOS_Network.pcapng
```

```output
-rw-r--r-- 1 root root 5496 Jul 27 04:27 /GLaDOS_Network.pcapng
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -q -z io,stat,1,COUNT -T fields -e tshark.appname 2>/dev/null | head
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -q -z endpoints,tcp 2>/dev/null | head
```

```output
================================================================================
TCP Endpoints
Filter:<No Filter>
                       |  Port  ||  Packets  | |  Bytes  | | Tx Packets | | Tx Bytes | | Rx Packets | | Rx Bytes |
192.168.132.1             54004          9           922          5             492           4             430   
192.168.132.133            8000          9           922          4             430           5             492   
================================================================================
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y "http" -T fields -e http.host 2>/dev/null | head
```

```output
192.168.132.133
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y "http && tcp.port==8000" -T fields -e http.request.full_uri 2>/dev/null | head
```

```output
http://192.168.132.133/
http://192.168.132.133/
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y "http && tcp.port==8000" -T fields -e http.request.full_uri -e http.method -e http.host -e http.request.uri 2>/dev/null
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y "tcp.port==8000" -T json 2>/dev/null | head -30
```

```output
[
  {
    "_index": "packets-2026-03-19",
    "_type": "doc",
    "_score": null,
    "_source": {
      "layers": {
        "frame": {
          "frame.section_number": "1",
          "frame.interface_id": "0",
          "frame.interface_id_tree": {
            "frame.interface_name": "\\Device\\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}",
            "frame.interface_description": "VMware Network Adapter VMnet8"
          },
          "frame.encap_type": "1",
          "frame.time": "Mar 19, 2026 23:41:43.736296500 UTC",
          "frame.time_utc": "Mar 19, 2026 23:41:43.736296500 UTC",
          "frame.time_epoch": "1773963703.736296500",
          "frame.offset_shift": "0.000000000",
          "frame.time_delta": "1.259668100",
          "frame.time_delta_displayed": "0.000000000",
          "frame.time_relative": "4.487980100",
          "frame.number": "12",
          "frame.len": "66",
          "frame.cap_len": "66",
          "frame.marked": "0",
          "frame.ignored": "0",
          "frame.protocols": "eth:ethertype:ip:tcp"
        },
        "eth": {
```

```bash
$ [bash] capinfos /GLaDOS_Network.pcapng
```

```output
File name:           /GLaDOS_Network.pcapng
File type:           Wireshark/... - pcapng
File encapsulation:  Ethernet
File timestamp precision:  nanoseconds (9)
Packet size limit:   file hdr: (not set)
Number of packets:   49
File size:           5496 bytes
Data size:           3397 bytes
Capture duration:    12.727491500 seconds
Earliest packet time: 2026-03-19 23:41:39.248316400
Latest packet time:   2026-03-19 23:41:51.975807900
Data byte rate:      266 bytes/s
Data bit rate:       2135 bits/s
Average packet size: 69.33 bytes
Average packet rate: 3 packets/s
SHA256:              4913b8460c5fdff54f3778274f42e98ccd430300666373dfc8f7f999b9170621
SHA1:                ffa8e7aeb840086e349544b7146b11fa7b81709e
Strict time order:   True
Capture hardware:    Intel(R) Xeon(R) E-2276M  CPU @ 2.80GHz (with SSE4.2)
Capture oper-sys:    64-bit Windows 11 (25H2), build 26200
Capture application: Dumpcap (Wireshark) 4.6.4 (v4.6.4-0-g93282876538d)
Number of interfaces in file: 1
Interface #0 info:
                     Name = \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}
                     Description = VMware Network Adapter VMnet8
                     Encapsulation = Ethernet (1 - ether)
                     Capture length = 262144
                     Time precision = nanoseconds (9)
                     Time ticks per second = 1000000000
                     Time resolution = 0x09
                     Operating system = 64-bit Windows 11 (25H2), build 26200
                     Number of stat entries = 1
                     Number of packets = 49
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y "http" -T fields -E separator=, -e http.content_type -e http.protocol -e http.request.full_uri -e http.response.code 2>/dev/null
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -V > /tmp/capture.txt 2>&1
```

```bash
$ [bash] head -100 /tmp/capture.txt
```

```output
Running as user "root" and group "root". This could be dangerous.
Frame 1: 42 bytes on wire (336 bits), 42 bytes captured (336 bits) on interface \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}, id 0
    Section number: 1
    Interface id: 0 (\Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D})
        Interface name: \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}
        Interface description: VMware Network Adapter VMnet8
    Encapsulation type: Ethernet (1)
    Arrival Time: Mar 19, 2026 23:41:39.248316400 UTC
    UTC Arrival Time: Mar 19, 2026 23:41:39.248316400 UTC
    Epoch Arrival Time: 1773963699.248316400
    [Time shift for this packet: 0.000000000 seconds]
    [Time delta from previous captured frame: 0.000000000 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 0.000000000 seconds]
    Frame Number: 1
    Frame Length: 42 bytes (336 bits)
    Capture Length: 42 bytes (336 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ethertype:arp]
Ethernet II, Src: VMware_c0:00:08 (00:50:56:c0:00:08), Dst: Broadcast (ff:ff:ff:ff:ff:ff)
    Destination: Broadcast (ff:ff:ff:ff:ff:ff)
        .... ..1. .... .... .... .... = LG bit: Locally administered address (this is NOT the factory default)
        .... ...1 .... .... .... .... = IG bit: Group address (multicast/broadcast)
    Source: VMware_c0:00:08 (00:50:56:c0:00:08)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = IG bit: I
…(截斷，共 5161 字)
```

```bash
$ [bash] grep -i http /tmp/capture.txt | head
```

```output
[Protocols in frame: eth:ethertype:ip:tcp:http:json]
    POST / HTTP/1.1\r\n
        Request Version: HTTP/1.1
    [Full request URI: http://192.168.132.133/]
    [Protocols in frame: eth:ethertype:ip:tcp:http:json:data-text-lines]
    HTTP/1.1 200 OK\r\n
        Response Version: HTTP/1.1
    [Full request URI: http://192.168.132.133/]
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.request.full_uri -e http.request.method -e http.response.full_uri -e http.http.frame_check -e http.file_data 2>/dev/null
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.cookie 2>/dev/null
```

```output
cake=Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ==
```

```bash
$ [python] import base64
import sys

encoded = "Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ=="
try:
    decoded = base64.b64decode(encoded)
    print(decoded)
except Exception as e:
    print(e)
```

```output
b'byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}'
```

```bash
$ [bash] strings /GLaDOS_Network.pcapng | grep -i flag
```

```bash
$ [python] import sys
try:
    import pyshark
    print('pyshark available')
except Exception as e:
    print(e)
```

```output
No module named 'pyshark'
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T json > /tmp/json.txt 2>&1
```

```bash
$ [bash] wc -l /tmp/json.txt
```

```output
398 /tmp/json.txt
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -q -z io,stat,1,COUNT -T fields -e _source.layers 2>/dev/null | head -20
```

```bash
$ [bash] head -1 /tmp/json.txt
```

```output
Running as user "root" and group "root". This could be dangerous.
```


**提交**：``　**正解**：`byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}`

---

### 第 2 次 (EPOCH 2) — solved=✅ C

```bash
$ [bash] ls -la /challenge
```

```output
ls: cannot access '/challenge': No such file or directory
```

```bash
$ [bash] find / -type f -name "*.pcapng" 2>/dev/null | head -20
```

```output
/GLaDOS_Network.pcapng
```

```bash
$ [bash] which tshark
```

```output
/usr/bin/tshark
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -T fields -e _ws.col.Info | head -20
```

```output
Running as user "root" and group "root". This could be dangerous.

Who has 192.168.132.133? Tell 192.168.132.1
192.168.132.133 is at 00:0c:29:b7:fb:48
NTP Version 4, client
Echo (ping) request  id=0x0000, seq=0/0, ttl=64
Echo (ping) reply    id=0x0000, seq=0/0, ttl=64 (request in 4)
Echo (ping) request  id=0x0000, seq=1/256, ttl=64
Echo (ping) reply    id=0x0000, seq=1/256, ttl=64 (request in 6)
NTP Version 4, client
Echo (ping) request  id=0x0000, seq=2/512, ttl=64
Echo (ping) reply    id=0x0000, seq=2/512, ttl=64 (request in 9)
NTP Version 4, client
54004 → 8000 [SYN] Seq=0 Win=65535 Len=0 MSS=1460 WS=256 SACK_PERM
8000 → 54004 [SYN, ACK] Seq=0 Ack=1 Win=64240 Len=0 MSS=1460 SACK_PERM WS=128
54004 → 8000 [ACK] Seq=1 Ack=1 Win=65280 Len=0
POST / HTTP/1.1 , JSON (application/json)
8000 → 54004 [ACK] Seq=1 Ack=211 Win=64128 Len=0
HTTP/1.1 200 OK 
HTTP/1.1 200 OK , JSON (application/json)
54004 → 8000 [ACK] Seq=211 Ack=198 Win=65280 Len=0
54004 → 8000 [RST, ACK] Seq=211 Ack=198 Win=0 Len=0
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y "http.request.method == POST" -T fields -e http.content_type -e http.content_length -e http.file_data 2>/dev/null | head -5
```

```output
application/json	24	7b224765744368616d6265724e756d626572223a2031377d
```

```bash
$ [python] import binascii, sys, base64, hashlib, json, re, string, os, subprocess, sys
hex_str = b'7b224765744368616d6265724e756d626572223a2031377d'
print(hex_str)
print(hex_str.decode('ascii'))
print(binascii.unhexlify(hex_str))
```

```output
b'7b224765744368616d6265724e756d626572223a2031377d'
7b224765744368616d6265724e756d626572223a2031377d
b'{"GetChamberNumber": 17}'
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y "http.response" -T fields -e http.file_data 2>/dev/null | head -5
```

```output
227b5c2254657374696e674368616d6265725c223a2031372c205c225374617475735c223a205c22436f6d706c6574655c227d22
```

```bash
$ [python] import binascii
hex_str = '227b5c2254657374696e674368616d6265725c223a2031372c205c225374617475735c223a205c22436f6d706c6574655c227d22'
data = binascii.unhexlify(hex_str)
print(data)
print(data.decode('utf-8', errors='replace'))
```

```output
b'"{\\"TestingChamber\\": 17, \\"Status\\": \\"Complete\\"}"'
"{\"TestingChamber\": 17, \"Status\": \"Complete\"}"
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.cookie -e http.set_cookie -e http.authorization -e http.user_agent 2>/dev/null | head -30
```

```output
cake=Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ==
```

```bash
$ [python] import base64, binascii
val = 'Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ=='
try:
    decoded = base64.b64decode(val)
    print(decoded)
    print(decoded.decode('utf-8', errors='replace'))
except Exception as e:
    print(e)
```

```output
b'byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}'
byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.cookie -E separator=, -E header=y | sort -u
```

```output
Running as user "root" and group "root". This could be dangerous.


cake=Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ==
http.cookie
```

```bash
$ [submit] byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```

```output
byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```


**提交**：`byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}`　**正解**：`byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}`

---

### 第 3 次 (EPOCH 3) — solved=❌ I

```bash
$ [bash] ls -la /challenge/
```

```output
ls: cannot access '/challenge/': No such file or directory
```

```bash
$ [bash] ls -la /
```

```output
total 20
drwxr-xr-x   1 root root   54 Jul 27 04:43 .
drwxr-xr-x   1 root root   54 Jul 27 04:43 ..
-rwxr-xr-x   1 root root    0 Jul 27 04:43 .dockerenv
-rw-r--r--   1 root root 5496 Jul 27 04:43 GLaDOS_Network.pcapng
lrwxrwxrwx   1 root root    7 Jul  4 09:05 bin -> usr/bin
drwxr-xr-x   1 root root    0 Jul  4 09:05 boot
drwxr-xr-x   5 root root  320 Jul 27 04:43 dev
drwxr-xr-x   1 root root   36 Jul 27 04:43 etc
drwxr-xr-x   1 root root    0 Jul  4 09:05 home
lrwxrwxrwx   1 root root    7 Jul  4 09:05 lib -> usr/lib
drwxr-xr-x   1 root root    0 Jul 13 00:00 media
drwxr-xr-x   1 root root    0 Jul 13 00:00 mnt
drwxr-xr-x   1 root root    0 Jul 13 00:00 opt
dr-xr-xr-x 378 root root    0 Jul 27 04:43 proc
drwx------   1 root root   20 Jul 14 02:07 root
drwxr-xr-x   1 root root   14 Jul 25 02:25 run
lrwxrwxrwx   1 root root    8 Jul  4 09:05 sbin -> usr/sbin
drwxr-xr-x   1 root root    0 Jul 13 00:00 srv
dr-xr-xr-x  11 root root    0 Jul 25 04:47 sys
drwxrwxrwt   1 root root    0 Jul 13 00:00 tmp
drwxr-xr-x   1 root root   18 Jul 13 00:00 usr
drwxr-xr-x   1 root root   22 Jul 13 00:00 var
```

```bash
$ [bash] cd / && ls -lh GLaDOS_Network.pcapng
```

```output
-rw-r--r-- 1 root root 5.4K Jul 27 04:43 GLaDOS_Network.pcapng
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -q -z io,stat,1
```

```output
Running as user "root" and group "root". This could be dangerous.


=============================
| IO Statistics             |
|                           |
| Duration: 12.727492 secs  |
| Interval:  1 secs         |
|                           |
| Col 1: Frames and bytes   |
|---------------------------|
|          |1               |
| Interval | Frames | Bytes |
|---------------------------|
|  0 <>  1 |      5 |   298 |
|  1 <>  2 |      3 |   196 |
|  2 <>  3 |      2 |   106 |
|  3 <>  4 |      1 |    90 |
|  4 <>  5 |     11 |  1028 |
|  5 <>  6 |      1 |    90 |
|  6 <>  7 |      6 |   314 |
|  7 <>  8 |      4 |   286 |
|  8 <>  9 |      3 |   196 |
|  9 <> 10 |      5 |   298 |
| 10 <> 11 |      2 |   180 |
| 11 <> 12 |      2 |   106 |
| 12 <> Dur|      4 |   209 |
=============================
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y http -T fields -e http.request.full_uri -e http.response.full_uri -e http.request.method -e http.response.code
```

```output
Running as user "root" and group "root". This could be dangerous.
tshark: Some fields aren't valid:
	http.response.full_uri
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y http -T fields -e http.request.full_uri -e http.response.full_uri -e http.request.method -e http.response.code
```

```output
Running as user "root" and group "root". This could be dangerous.
tshark: Some fields aren't valid:
	http.response.full_uri
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y http -T fields -e http.request.full_uri -e http.request.uri -e http.request.method -e http.response.code
```

```output
Running as user "root" and group "root". This could be dangerous.

http://192.168.132.133/	/	POST	
http://192.168.132.133/	/		200
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y "http.request.method == POST" -T fields -e _ws.col.Info
```

```output
Running as user "root" and group "root". This could be dangerous.

POST / HTTP/1.1 , JSON (application/json)
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y "http.request.method == POST" -XX
```

```output
Running as user "root" and group "root". This could be dangerous.

   15 4.488707400 192.168.132.1 → 192.168.132.133 HTTP/JSON 264 POST / HTTP/1.1 , JSON (application/json)
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y "http.request.method == POST" -V
```

```output
Running as user "root" and group "root". This could be dangerous.

Frame 15: 264 bytes on wire (2112 bits), 264 bytes captured (2112 bits) on interface \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}, id 0
    Section number: 1
    Interface id: 0 (\Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D})
        Interface name: \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}
        Interface description: VMware Network Adapter VMnet8
    Encapsulation type: Ethernet (1)
    Arrival Time: Mar 19, 2026 23:41:43.737023800 UTC
    UTC Arrival Time: Mar 19, 2026 23:41:43.737023800 UTC
    Epoch Arrival Time: 1773963703.737023800
    [Time shift for this packet: 0.000000000 seconds]
    [Time delta from previous captured frame: 0.000170100 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 4.488707400 seconds]
    Frame Number: 15
    Frame Length: 264 bytes (2112 bits)
    Capture Length: 264 bytes (2112 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ethertype:ip:tcp:http:json]
Ethernet II, Src: VMware_c0:00:08 (00:50:56:c0:00:08), Dst: VMware_b7:fb:48 (00:0c:29:b7:fb:48)
    Destination: VMware_b7:fb:48 (00:0c:29:b7:fb:48)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Source: VMware_c0:00:08 (00:50:56:c0:00:08)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = I
…(截斷，共 5182 字)
```

```bash
$ [python] import base64, json, binascii, sys
b64 = 'Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ=='
try:
    decoded = base64.b64decode(b64)
    print('Decoded bytes:', decoded)
    print('As string:', decoded.decode('utf-8', errors='replace'))
except Exception as e:
    print('Error:', e)
```

```output
Decoded bytes: b'byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}'
As string: byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y http -T fields -e http.request.method -e http.request.uri -e http.response.code
```

```output
Running as user "root" and group "root". This could be dangerous.

POST	/	
	/	200
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y "http.request" -T fields -e frame.number -e http.request.uri
```

```output
Running as user "root" and group "root". This could be dangerous.

15	/
```

```bash
$ [python] import base64, json, re
b64 = 'Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ=='
decoded = base64.b64decode(b64)
print('Decoded length:', len(decoded))
print('Decoded:', decoded)
# Try JWK
# maybe it's JWE? There's 4812... looking like a flag.
# Split by dots? There are no dots.
print('As UTF-8:', decoded.decode('utf-8'))
```

```output
Decoded length: 34
Decoded: b'byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}'
As UTF-8: byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```

```bash
$ [bash] which jq
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -T fields -e frame.number
```

```output
Running as user "root" and group "root". This could be dangerous.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y http -V > /tmp/http.txt 2>/dev/null || echo "failed"
```

```bash
$ [bash] grep -i flag /tmp/http.txt
```

```output
010. .... = Flags: 0x2, Don't fragment
        [Completeness Flags: ···ASS]
    Flags: 0x018 (PSH, ACK)
        [TCP Flags: ·······AP···]
        [Bytes sent since last PSH flag: 210]
    010. .... = Flags: 0x2, Don't fragment
        [Completeness Flags: ··DASS]
    Flags: 0x019 (FIN, PSH, ACK)
        [TCP Flags: ·······AP··F]
        [Bytes sent since last PSH flag: 52]
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -T fields -e _ws.col.Protocol | sort -u
```

```output
Running as user "root" and group "root". This could be dangerous.

ARP
HTTP/JSON
ICMP
NTP
TCP
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -R 'http.request.method == "POST"' -T fields -e http.request.uri
```

```output
Running as user "root" and group "root". This could be dangerous.
tshark: -R without -2 is deprecated. For single-pass filtering use -Y.
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -Y 'http.request.method == "POST"' -T fields -e http.request.uri
```

```output
Running as user "root" and group "root". This could be dangerous.

/
```

```bash
$ [bash] strings GLaDOS_Network.pcapng | grep -i flag
```

```bash
$ [bash] tshark -r GLaDOS_Network.pcapng -V > /tmp/full.txt 2>/dev/null; head -200 /tmp/full.txt
```

```output
Frame 1: 42 bytes on wire (336 bits), 42 bytes captured (336 bits) on interface \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}, id 0
    Section number: 1
    Interface id: 0 (\Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D})
        Interface name: \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}
        Interface description: VMware Network Adapter VMnet8
    Encapsulation type: Ethernet (1)
    Arrival Time: Mar 19, 2026 23:41:39.248316400 UTC
    UTC Arrival Time: Mar 19, 2026 23:41:39.248316400 UTC
    Epoch Arrival Time: 1773963699.248316400
    [Time shift for this packet: 0.000000000 seconds]
    [Time delta from previous captured frame: 0.000000000 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 0.000000000 seconds]
    Frame Number: 1
    Frame Length: 42 bytes (336 bits)
    Capture Length: 42 bytes (336 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ethertype:arp]
Ethernet II, Src: VMware_c0:00:08 (00:50:56:c0:00:08), Dst: Broadcast (ff:ff:ff:ff:ff:ff)
    Destination: Broadcast (ff:ff:ff:ff:ff:ff)
        .... ..1. .... .... .... .... = LG bit: Locally administered address (this is NOT the factory default)
        .... ...1 .... .... .... .... = IG bit: Group address (multicast/broadcast)
    Source: VMware_c0:00:08 (00:50:56:c0:00:08)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Type: ARP (0x0806)
    [Stream ind
…(截斷，共 9920 字)
```

```bash
$ [stateful_python] s = "byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}"
print(len(s))
print(s)
```


**提交**：``　**正解**：`byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}`

---

### 第 4 次 (EPOCH 4) — solved=✅ C

```bash
$ [bash] ls -la /challenge
```

```output
ls: cannot access '/challenge': No such file or directory
```

```bash
$ [bash] pwd
```

```output
/
```

```bash
$ [bash] find / -name "GLaDOS_Network.pcapng" 2>/dev/null
```

```output
/GLaDOS_Network.pcapng
```

```bash
$ [bash] strings /GLaDOS_Network.pcapng | head -30
```

```output
Intel(R) Xeon(R) E-2276M  CPU @ 2.80GHz (with SSE4.2)
64-bit Windows 11 (25H2), build 26200
Dumpcap (Wireshark) 4.6.4 (v4.6.4-0-g93282876538d)
\Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}
VMware Network Adapter VMnet8
64-bit Windows 11 (25H2), build 26200
Ynl1
byuc
Ynl1
byuc
Y3Rm
tf{T
Y3Rm
tf{T
lAaZ
e1Ro
urr3
e1Ro
urr3
8:h#
 "aL
 "aL
POST / HTTP/1.1
Host: 192.168.132.133
Cookie: cake=Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ==
X-Seq: 0
Content-Type: application/json
Content-Length: 24
Connection: close
{"GetChamberNumber": 17}(
```

```bash
$ [python] import base64
s = "Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ=="
try:
    decoded = base64.b64decode(s)
    print(decoded)
    print(decoded.decode())
except Exception as e:
    print(e)
```

```output
b'byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}'
byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```

```bash
$ [bash] grep -a "tf{" /GLaDOS_Network.pcapng
```

```output
           eS�b    eS�y    eS�u    eS�c      |      P       �b�8�$.   .    )��H PV�  E      @pYnl1����  #    byuc  P      \       �b���!$<   <    PV�O� )��H E   �  @������Ynl1  (#    byuc              \      P       �b�`�L.   .    )��H PV�  E      @�Y3Rm���� D   tf{T  P      \       �b��"L<   <    PV�O� )��H E   !l  @h�����Y3Rm  D   tf{T              \      |       �b� lAaZ   Z    )��H PV�  E  L   @��������� {4 8:#
```

```bash
$ [bash] ls -lh /GLaDOS_Network.pcapng
```

```output
-rw-r--r-- 1 root root 5.4K Jul 27 04:51 /GLaDOS_Network.pcapng
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.cookie 2>/dev/null | head -20
```

```output
cake=Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ==
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.file_data 2>/dev/null
```

```output
7b224765744368616d6265724e756d626572223a2031377d
227b5c2254657374696e674368616d6265725c223a2031372c205c225374617475735c223a205c22436f6d706c6574655c227d22
```

```bash
$ [python] import binascii
field1 = "7b224765744368616d6265724e756d6265724e756d626572223a2031377d"
field2 = "227b2254657374696e674368616d6265725c223a2031372c205c225374617475735c223a205c22436f6d706c6574655c227d22"
# decode hex to ascii
try:
    bytes1 = binascii.unhexlify(field1)
    print('field1:', bytes1.decode())
except Exception as e:
    print('field1 error:', e)
try:
    bytes2 = binascii.unhexlify(field2)
    print('field2:', bytes2.decode())
except Exception as e:
    print('field2 error:', e)
```

```output
field1: {"GetChamberNumberNumber": 17}
field2: "{"TestingChamber\": 17, \"Status\": \"Complete\"}"
```

```bash
$ [bash] strings /GLaDOS_Network.pcapng | grep -i flag
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.cookie
```

```output
Running as user "root" and group "root". This could be dangerous.

cake=Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ==
```

```bash
$ [submit] byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```

```output
byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```


**提交**：`byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}`　**正解**：`byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}`

---

### 第 5 次 (EPOCH 5) — solved=❌ I

```bash
$ [bash] ls -la /challenge/
```

```output
ls: cannot access '/challenge/': No such file or directory
```

```bash
$ [bash] ls -la /
```

```output
total 20
drwxr-xr-x   1 root root   54 Jul 27 05:02 .
drwxr-xr-x   1 root root   54 Jul 27 05:02 ..
-rwxr-xr-x   1 root root    0 Jul 27 05:02 .dockerenv
-rw-r--r--   1 root root 5496 Jul 27 05:02 GLaDOS_Network.pcapng
lrwxrwxrwx   1 root root    7 Jul  4 09:05 bin -> usr/bin
drwxr-xr-x   1 root root    0 Jul  4 09:05 boot
drwxr-xr-x   5 root root  320 Jul 27 05:02 dev
drwxr-xr-x   1 root root   36 Jul 27 05:02 etc
drwxr-xr-x   1 root root    0 Jul  4 09:05 home
lrwxrwxrwx   1 root root    7 Jul  4 09:05 lib -> usr/lib
drwxr-xr-x   1 root root    0 Jul 13 00:00 media
drwxr-xr-x   1 root root    0 Jul 13 00:00 mnt
drwxr-xr-x   1 root root    0 Jul 13 00:00 opt
dr-xr-xr-x 376 root root    0 Jul 27 05:02 proc
drwx------   1 root root   20 Jul 14 02:07 root
drwxr-xr-x   1 root root   14 Jul 25 02:25 run
lrwxrwxrwx   1 root root    8 Jul  4 09:05 sbin -> usr/sbin
drwxr-xr-x   1 root root    0 Jul 13 00:00 srv
dr-xr-xr-x  11 root root    0 Jul 25 04:47 sys
drwxrwxrwt   1 root root    0 Jul 13 00:00 tmp
drwxr-xr-x   1 root root   18 Jul 13 00:00 usr
drwxr-xr-x   1 root root   22 Jul 13 00:00 var
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -T fields -e frame.number -c 5
```

```output
Running as user "root" and group "root". This could be dangerous.

1
2
3
4
5
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.method -e http.request.uri -e http.host | head -20
```

```output
Running as user "root" and group "root". This could be dangerous.
tshark: Some fields aren't valid:
	http.method
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.request.full_uri | head -10
```

```output
Running as user "root" and group "root". This could be dangerous.

http://192.168.132.133/
http://192.168.132.133/
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http | wc -l
```

```output
Running as user "root" and group "root". This could be dangerous.

2
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -T fields -e frame.number -e frame.time -e frame.protocols -e frame.len -e pkt_src -e pkt_dst | head -20
```

```output
Running as user "root" and group "root". This could be dangerous.
tshark: Some fields aren't valid:
	pkt_dst
	pkt_src
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y "tcp" -T fields -e tcp.data | head -5
```

```output
Running as user "root" and group "root". This could be dangerous.
tshark: Some fields aren't valid:
	tcp.data
```

```bash
$ [python] import sys
from scapy.all import rdpcap
import re

packets = rdpcap('/GLaDOS_Network.pcapng')
flag_candidates = []
for pkt in packets:
    if pkt.haslayer('TCP'):
        try:
            payload = bytes(pkt[TCP].payload)
            # check if payload is printable
            if all(32 <= b <= 126 for b in payload):
                s = payload.decode('utf-8', errors='ignore')
                # look for flag pattern
                if re.search(r'CTF\{.*\}', s, re.IGNORECASE):
                    print('Found possible flag in TCP packet:', s)
                line = s.strip()
                if 'CTF{' in line or 'flag' in line.lower():
                    flag_candidates.append(line)
        except Exception as e:
            pass
print('All candidate strings:', flag_candidates)
```

```output
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
ModuleNotFoundError: No module named 'scapy'
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -q -z io,phs -c 2
```

```output
Running as user "root" and group "root". This could be dangerous.


===================================================================
Protocol Hierarchy Statistics
Filter: 

eth                                      frames:2 bytes:102
  arp                                    frames:2 bytes:102
===================================================================
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -V | head -30
```

```output
Running as user "root" and group "root". This could be dangerous.

Frame 15: 264 bytes on wire (2112 bits), 264 bytes captured (2112 bits) on interface \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}, id 0
    Section number: 1
    Interface id: 0 (\Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D})
        Interface name: \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}
        Interface description: VMware Network Adapter VMnet8
    Encapsulation type: Ethernet (1)
    Arrival Time: Mar 19, 2026 23:41:43.737023800 UTC
    UTC Arrival Time: Mar 19, 2026 23:41:43.737023800 UTC
    Epoch Arrival Time: 1773963703.737023800
    [Time shift for this packet: 0.000000000 seconds]
    [Time delta from previous captured frame: 0.000170100 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 4.488707400 seconds]
    Frame Number: 15
    Frame Length: 264 bytes (2112 bits)
    Capture Length: 264 bytes (2112 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ethertype:ip:tcp:http:json]
Ethernet II, Src: VMware_c0:00:08 (00:50:56:c0:00:08), Dst: VMware_b7:fb:48 (00:0c:29:b7:fb:48)
    Destination: VMware_b7:fb:48 (00:0c:29:b7:fb:48)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Source: VMware_c0:00:08 (00:50:56:c0:00:08)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = I
…(截斷，共 1778 字)
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T json > /tmp/http.json
```

```output
Running as user "root" and group "root". This could be dangerous.
```

```bash
$ [bash] cat /tmp/http.json | head -20
```

```output
[
  {
    "_index": "packets-2026-03-19",
    "_type": "doc",
    "_score": null,
    "_source": {
      "layers": {
        "frame": {
          "frame.section_number": "1",
          "frame.interface_id": "0",
          "frame.interface_id_tree": {
            "frame.interface_name": "\\Device\\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}",
            "frame.interface_description": "VMware Network Adapter VMnet8"
          },
          "frame.encap_type": "1",
          "frame.time": "Mar 19, 2026 23:41:43.737023800 UTC",
          "frame.time_utc": "Mar 19, 2026 23:41:43.737023800 UTC",
          "frame.time_epoch": "1773963703.737023800",
          "frame.offset_shift": "0.000000000",
          "frame.time_delta": "0.000170100",
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e http.response.code | sort -u
```

```output
Running as user "root" and group "root". This could be dangerous.


200
```

```bash
$ [bash] tshark -G fields | grep http
```

```output
The output of your call to bash was too long to be displayed.
Here is a truncated version:
<START_TOOL_OUTPUT>
Running as user "root" and group "root". This could be dangerous.

F	HTTP Headers	btatt.http_headers	FT_STRING	btatt		0x0	
F	HTTP Status Code	btatt.http_status_code	FT_UINT16	btatt	BASE_DEC	0x0	
F	HTTP Data Status	btatt.http_data_status	FT_UINT8	btatt	BASE_HEX	0x0	
F	Headers Received	btatt.http_data_status.headers_received	FT_BOOLEAN	btatt	8	0x1	
F	Headers Truncated	btatt.http_data_status.headers_truncated	FT_BOOLEAN	btatt	8	0x2	
F	Body Received	btatt.http_data_status.body_received	FT_BOOLEAN	btatt	8	0x4	
F	Body Truncated	btatt.http_data_status.body_truncated	FT_BOOLEAN	btatt	8	0x8	
F	Reserved	btatt.http_data_status.reserved	FT_UINT8	btatt	BASE_HEX	0xf0	
F	HTTP Entity Body	btatt.http_entity_body	FT_STRING	btatt		0x0	
F	HTTPS Security	btatt.https_security	FT_UINT8	btatt	BASE_HEX	0x0	
F	IP address	dect_mitel_rfp.sys.http_set.ip_address	FT_IPv6	dect_mitel_rfp		0x0	
F	Port	dect_mitel_rfp.sys.http_set.port	FT_UINT16	dect_mitel_rfp	BASE_DEC	0x0	
F	HTTPSRVR	dhcp.option.vendor.avaya.httpsrvr	FT_STRINGZ	dhcp		0x0	Option 242: HTTPSRVR (HTTP server(s) to download configuration)
F	HTTPDIR	dhcp.option.vendor.avaya.httpdir	FT_STRINGZ	dhcp		0x0	Option 242: HTTPDIR (Path to configuration files)
F	Vulnerable to dictionary attacks. If possible, change EAP type. See http://www.cisco.com/warp/public/cc/pd/witc/ao350ap/prodlit/2331_pp.pdf	eap.dictionary_attacks	FT_NONE	eap		0x0	
F	TCP Port	epm.proto.http_port	FT_UINT16	epm	BASE_DEC	0x0	TCP Port where this service can be found
P	Hyperte
…(截斷，共 32897 字)
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -T fields -e frame.number -c 10
```

```output
Running as user "root" and group "root". This could be dangerous.
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -T fields -e frame.number -e frame.protocols -c 10
```

```output
Running as user "root" and group "root". This could be dangerous.

1	eth:ethertype:arp
2	eth:ethertype:arp
3	eth:ethertype:ip:udp:ntp
4	eth:ethertype:ip:icmp:data
5	eth:ethertype:ip:icmp:data
6	eth:ethertype:ip:icmp:data
7	eth:ethertype:ip:icmp:data
8	eth:ethertype:ip:udp:ntp
9	eth:ethertype:ip:icmp:data
10	eth:ethertype:ip:icmp:data
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -q -z io,phs -c 200
```

```output
Running as user "root" and group "root". This could be dangerous.


===================================================================
Protocol Hierarchy Statistics
Filter: 

eth                                      frames:49 bytes:3397
  arp                                    frames:6 bytes:306
  ip                                     frames:43 bytes:3091
    udp                                  frames:10 bytes:900
      ntp                                frames:10 bytes:900
    icmp                                 frames:24 bytes:1269
    tcp                                  frames:9 bytes:922
      http                               frames:2 bytes:370
        json                             frames:2 bytes:370
          data-text-lines                frames:1 bytes:106
            tcp.segments                 frames:1 bytes:106
===================================================================
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -Y http -V -c 2
```

```output
Running as user "root" and group "root". This could be dangerous.
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -T fields -e frame.number -e frame.time -e frame.protocols -e frame.len | head -30
```

```output
Running as user "root" and group "root". This could be dangerous.

1	Mar 19, 2026 23:41:39.248316400 UTC	eth:ethertype:arp	42
2	Mar 19, 2026 23:41:39.248719800 UTC	eth:ethertype:arp	60
3	Mar 19, 2026 23:41:39.249693200 UTC	eth:ethertype:ip:udp:ntp	90
4	Mar 19, 2026 23:41:40.221043000 UTC	eth:ethertype:ip:icmp:data	46
5	Mar 19, 2026 23:41:40.221376500 UTC	eth:ethertype:ip:icmp:data	60
6	Mar 19, 2026 23:41:40.891535200 UTC	eth:ethertype:ip:icmp:data	46
7	Mar 19, 2026 23:41:40.891886300 UTC	eth:ethertype:ip:icmp:data	60
8	Mar 19, 2026 23:41:41.246848000 UTC	eth:ethertype:ip:udp:ntp	90
9	Mar 19, 2026 23:41:42.115594300 UTC	eth:ethertype:ip:icmp:data	46
10	Mar 19, 2026 23:41:42.115970100 UTC	eth:ethertype:ip:icmp:data	60
11	Mar 19, 2026 23:41:42.476628400 UTC	eth:ethertype:ip:udp:ntp	90
12	Mar 19, 2026 23:41:43.736296500 UTC	eth:ethertype:ip:tcp	66
13	Mar 19, 2026 23:41:43.736713600 UTC	eth:ethertype:ip:tcp	66
14	Mar 19, 2026 23:41:43.736853700 UTC	eth:ethertype:ip:tcp	54
15	Mar 19, 2026 23:41:43.737023800 UTC	eth:ethertype:ip:tcp:http:json	264
16	Mar 19, 2026 23:41:43.737303700 UTC	eth:ethertype:ip:tcp	60
17	Mar 19, 2026 23:41:43.738623800 UTC	eth:ethertype:ip:tcp	198
18	Mar 19, 2026 23:41:43.738767800 UTC	eth:ethertype:ip:tcp:http:json:data-text-lines	106
19	Mar 19, 2026 23:41:43.739590100 UTC	eth:ethertype:ip:tcp	54
20	Mar 19, 2026 23:41:43.739727600 UTC	eth:ethertype:ip:tcp	54
21	Mar 19, 2026 23:41:43.903522800 UTC	eth:ethertype:ip:icmp:data	46
22	Mar 19, 2026 23:41:43.903880200 UTC	eth:ethertype:ip:icmp:data	60
23	Mar 19, 2026 23:41:44.362656400 UTC	eth:ethertype:ip:udp:ntp
…(截斷，共 2066 字)
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -V -Y "frame.number == 15"
```

```output
Running as user "root" and group "root". This could be dangerous.

Frame 15: 264 bytes on wire (2112 bits), 264 bytes captured (2112 bits) on interface \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}, id 0
    Section number: 1
    Interface id: 0 (\Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D})
        Interface name: \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}
        Interface description: VMware Network Adapter VMnet8
    Encapsulation type: Ethernet (1)
    Arrival Time: Mar 19, 2026 23:41:43.737023800 UTC
    UTC Arrival Time: Mar 19, 2026 23:41:43.737023800 UTC
    Epoch Arrival Time: 1773963703.737023800
    [Time shift for this packet: 0.000000000 seconds]
    [Time delta from previous captured frame: 0.000170100 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 4.488707400 seconds]
    Frame Number: 15
    Frame Length: 264 bytes (2112 bits)
    Capture Length: 264 bytes (2112 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ethertype:ip:tcp:http:json]
Ethernet II, Src: VMware_c0:00:08 (00:50:56:c0:00:08), Dst: VMware_b7:fb:48 (00:0c:29:b7:fb:48)
    Destination: VMware_b7:fb:48 (00:0c:29:b7:fb:48)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Source: VMware_c0:00:08 (00:50:56:c0:00:08)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = I
…(截斷，共 5182 字)
```

```bash
$ [python] import base64
cookie = 'Ynl1Y3Rme1RoM19DNGszXyFzXzRfTCEzX0hUQzU2emVFfQ=='
try:
    decoded = base64.b64decode(cookie)
    print('Decoded bytes:', decoded)
    print('Decoded as string (utf-8):', decoded.decode('utf-8', errors='ignore'))
except Exception as e:
    print(e)
```

```output
Decoded bytes: b'byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}'
Decoded as string (utf-8): byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}
```

```bash
$ [bash] tshark -G fields | grep -i tcp | head -20
```

```output
Running as user "root" and group "root". This could be dangerous.

F	TCP	alljoyn.whohas.T	FT_BOOLEAN	ajns	8	0x8	
F	TCP	alljoyn.isat.T	FT_BOOLEAN	ajns	8	0x8	
F	IPv6 TCP	alljoyn.isat.R6	FT_BOOLEAN	ajns	8	0x2	
F	IPv4 TCP	alljoyn.isat.R4	FT_BOOLEAN	ajns	8	0x8	
F	TCP Transport	alljoyn.isat.TransportMask.TCP	FT_BOOLEAN	ajns	16	0x4	
F	Register TCP Timeout	5co_legacy.RegTCPTimeout	FT_UINT8	5co_legacy	BASE_CUSTOM	0x0	
F	Write register 0x14 (Name: TCP Timeout, Size: 1)	5co_rap.RegTCPTimeout.write	FT_UINT8	5co_rap	BASE_CUSTOM	0x0	
F	Read answer register 0x14 (Name: TCP Timeout, Size: 1)	5co_rap.RegTCPTimeout.readanswer	FT_UINT8	5co_rap	BASE_CUSTOM	0x0	
F	pTCParticipants	HI2Operations.pTCParticipants	FT_STRING	HI2operations		0x0	UTF8String
F	pTCParty	HI2Operations.pTCParty	FT_STRING	HI2operations		0x0	UTF8String
F	pTCPartyDrop	HI2Operations.pTCPartyDrop	FT_STRING	HI2operations		0x0	UTF8String
F	BSC RSL TCP Port	gsm_abis_oml.fom.attr.ipa.rsl_port	FT_UINT16	gsm_abis_oml	BASE_DEC	0x0	Port number to which the BST establishes the RSL link
F	Primary OML TCP Port	gsm_abis_oml.fom.attr.ipa.prim_oml_port	FT_UINT16	gsm_abis_oml	BASE_DEC	0x0	TCP Port of the BSC for the primary OML link
F	Data length	rdmnet.tcp_length	FT_UINT32	rdmnet	BASE_DEC	0x0	TCP data size in bytes
F	Client TCP Inactive	rdmnet.llrp.probe_request.filter_client_tcp_inactive	FT_BOOLEAN	rdmnet	8	0x1	Client TCP inactive flag
F	IPv4 TCP Port	rdmnet.broker.redirect_ipv4.tcp_port	FT_UINT16	rdmnet	BASE_DEC	0x0	Redirect IPv4 TCP port
F	TCP Port	rdmnet.broker.redirect_ipv6.tcp_port	FT_UINT16	rdmnet	BASE_DEC	0x0	Redirect IPv6 TCP port
F	
…(截斷，共 1832 字)
```

```bash
$ [bash] tshark -r /GLaDOS_Network.pcapng -V -Y "frame.number == 4"
```

```output
Running as user "root" and group "root". This could be dangerous.

Frame 4: 46 bytes on wire (368 bits), 46 bytes captured (368 bits) on interface \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}, id 0
    Section number: 1
    Interface id: 0 (\Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D})
        Interface name: \Device\NPF_{CDA6A612-BB85-4C72-BB0A-F44DBB5E070D}
        Interface description: VMware Network Adapter VMnet8
    Encapsulation type: Ethernet (1)
    Arrival Time: Mar 19, 2026 23:41:40.221043000 UTC
    UTC Arrival Time: Mar 19, 2026 23:41:40.221043000 UTC
    Epoch Arrival Time: 1773963700.221043000
    [Time shift for this packet: 0.000000000 seconds]
    [Time delta from previous captured frame: 0.971349800 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 0.972726600 seconds]
    Frame Number: 4
    Frame Length: 46 bytes (368 bits)
    Capture Length: 46 bytes (368 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ethertype:ip:icmp:data]
Ethernet II, Src: VMware_c0:00:08 (00:50:56:c0:00:08), Dst: VMware_b7:fb:48 (00:0c:29:b7:fb:48)
    Destination: VMware_b7:fb:48 (00:0c:29:b7:fb:48)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Source: VMware_c0:00:08 (00:50:56:c0:00:08)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
        .... ...0 .... .... .... .... = IG bit: Individ
…(截斷，共 2912 字)
```


**提交**：``　**正解**：`byuctf{Th3_C4k3_!s_4_L!3_HTC56zeE}`