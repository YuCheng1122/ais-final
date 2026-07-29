# Writeup — VaultDoor Training (picoCTF, rev/easy)

## 辨識

題目附上一份 `VaultDoorTraining.java`。`main()` 把使用者輸入 `userInput` 用
`userInput.substring("picoCTF{".length(), userInput.length()-1)` 去頭去尾，只留 `picoCTF{...}`
大括號內的內容當作 `input`，再交給 `checkPassword(input)` 驗證。因此真正的密碼就是
`checkPassword` 內比對的字串，flag 即 `picoCTF{` + 該字串 + `}`。

## 解法

直接 `cat` 原始碼，閱讀 `checkPassword` 函式即可——密碼是硬編碼在 `equals()` 裡的字面值：

```bash
cat VaultDoorTraining.java
```

```java
public boolean checkPassword(String password) {
    return password.equals("w4rm1ng_Up_w1tH_jAv4_be8d9806f18");
}
```

不需要編譯或執行，把字面值 `w4rm1ng_Up_w1tH_jAv4_be8d9806f18` 套回 `picoCTF{...}` 外框即得 flag。
（原始碼註解也自嘲把密碼寫死在原始碼裡並不安全。）

## Flag

`picoCTF{w4rm1ng_Up_w1tH_jAv4_be8d9806f18}`
