# Writeup — Modified Metadata (picoCTF, forensics/medium)

## 辨識

題目給一張 `cat.jpg` 並提示「檔案可以被祕密地改動」，指向被竄改的影像中繼資料（metadata）。JPEG 的 EXIF / XMP 欄位可被任意填寫，是常見的藏 flag 位置，因此改用 `exiftool` 檢視所有中繼欄位，而非直接看圖。

## 解法

用 `exiftool` 傾印中繼資料：

```bash
exiftool cat.jpg
```

會看到 `Copyright Notice` 寫著 `PicoCTF`，而 `License` 欄位是一串明顯的 base64：

```text
Copyright Notice : PicoCTF
License          : cGljb0NURnt0aGVfbTN0YWRhdGFfMXNfbW9kaWZpZWR9
```

`License` 的值不是正常授權字串，長度與字元組成都像 base64。直接解碼：

```bash
echo cGljb0NURnt0aGVfbTN0YWRhdGFfMXNfbW9kaWZpZWR9 | base64 -d
```

輸出即為 flag。（原始 writeup 需先從 `exiftool_download_url.txt` 下載 `exiftool`，此處假設環境已有該工具。）

## Flag

`picoCTF{the_m3tadata_1s_modified}`
