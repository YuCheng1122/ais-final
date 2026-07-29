# Writeup — find the hidden file (picoCTF, misc/easy)

## 辨識

題目要求「Unzip this archive and find the file named 'uber-secret.txt'」。這是 `find` 指令的
基本操作題：解壓後 flag 藏在以 `.` 開頭的隱藏目錄裡，一般 `ls` 不會顯示，需用 `find` 或 `ls -a` 遞迴尋找。

## 解法

解壓縮後直接用 `find` 依檔名搜尋，`cat` 出內容即可：

```bash
unzip files.zip
find files -name 'uber-secret.txt'
# files/adequate_books/more_books/.secret/deeper_secrets/deepest_secrets/uber-secret.txt
cat files/adequate_books/more_books/.secret/deeper_secrets/deepest_secrets/uber-secret.txt
```

目標檔位於多層隱藏路徑 `.secret/deeper_secrets/deepest_secrets/` 之下，內容即為明文 flag。

## Flag

`picoCTF{f1nd_15_f457_ab443fd1}`
