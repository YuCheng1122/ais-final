# Writeup — tic-tac-no (LACTF 2026, pwn/easy)

## 漏洞：越界 index 導致全域寫

三個全域變數在 `chall.c` 開頭連續宣告，記憶體上緊鄰：

```c
char board[9];      // 偏移 +0..+8
char player = 'X';  // 偏移 +9
char computer = 'O';// 偏移 +10
```

`playerMove()` 由使用者兩個整數算 index，檢查邏輯反了：

```c
int index = (x-1)*3+(y-1);
if(index >= 0 && index < 9 && board[index] != ' '){
    printf("Invalid move.\n");
}else{
    board[index] = player;   // index<0 或 index>=9 時無條件越界寫 'X'
    break;
}
```

只有「index 在 `[0,9)` 且該格已被佔用」才算 invalid。任何 `index < 0` 或 `index >= 9` 都走 else 分支，把 `player`（`'X'`）寫進 `board[index]`——這是一個以 index 為位移、寫入固定值 `'X'` 的越界寫原語。`scanf("%d")` 不限制範圍，故 index 可為任意值。

## 勝利條件

`main()` 迴圈結束後：

```c
if (winner == player) {   // winner=='X'
    // fopen("flag.txt") 並印出
}
```

`checkWin()` 只要任一行/列/對角三格相等且非空白就回傳該字元。所以我們需要讓某條線變成三個 `'X'`，且 `winner == player('X')`。

## 攻擊：用 index 10 覆寫 `computer`

`board` 偏移 +10 正好是 `computer`。要命中 index 10：

```
(x-1)*3 + (y-1) = 10   =>  x=4, y=2   (即 3*3 + 1 = 10)
```

第一手輸入 `row=4, col=2`，越界寫使 `computer` 從 `'O'` 變成 `'X'`。此後 `player == computer == 'X'`：

- `perfectComputerMove()` 呼叫 `minimax`，而 `minimax` 用 `computer`/`player` 判斷勝負，兩者都變 `'X'`，bot 只會再放 `'X'`，永遠無法幫對手（也就無法擋你、也無法自成一線贏你）。
- 棋盤上每一格都是 `'X'`。

之後隨便下幾手合法的盤內位置，很快湊出一條三 `'X'` 直線，`checkWin()` 回傳 `'X'`，`winner == player`，程式開啟 `flag.txt` 並印出。

## 打法（互動輸入序列）

```
> row=4  col=2        # index 10：computer := 'X'
> row=1  col=1        # board[0]='X'
（bot 回一手 'X'）
> row=1  col=2        # board[1]='X'
（bot 回一手 'X'）
> row=1  col=3        # board[2]='X'  -> 第一列三個 'X' -> win
```

由於 bot 也在放 `'X'`，實際只需補足任一條線的空格即可；最壞情況下棋盤全 `'X'`、`checkWin` 立即成立。程式印出 flag。

## Flag

`lactf{th3_0nly_w1nn1ng_m0ve_1s_t0_p1ay}`
