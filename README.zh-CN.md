# mcp-env-preflight

这是一个 Python 3.11+ 离线命令行工具，用于检查调用方提供的 MCP 配置文本中的环境变量占位符。它只使用明确提供的名称列表，不读取进程环境，也不展开或替换任何值。

## 输入与行为

从标准输入接收一个严格 UTF-8 JSON 对象，最大 256 KiB。顶层键必须恰好为 `values`、`declared_names`、`ambient_names`。`values` 是 1–64 个字符串组成的数组，每个字符串最多 4096 个 Unicode 码点。两个名称数组各最多 128 个不重复名称，名称必须符合 ASCII 正则 `[A-Za-z_][A-Za-z0-9_]{0,127}`。

支持的占位符子集为 `$NAME`、`${NAME}`、`${NAME:-fallback}`。fallback 可以为空，并在下一个 `}` 处结束；不能嵌套 `${...}`。工具只扫描文本，不是完整的 shell、dotenv、JSON 或 MCP 客户端解析器。格式错误或不支持的花括号占位符会被拒绝。单独的 `$` 或后面没有合法名称的 `$` 保留为普通文本。

每个匹配项输出 1 起始的 `ordinal`、变量 `name` 和 `source`：`declared` 优先于 `ambient`；仅当名称不在这两个列表中且语法带有 fallback 时才返回 `fallback`；否则是 `missing`。不会输出配置文本、fallback 内容、路径或操作系统环境数据。结果按输入值顺序及字符串内位置排序。最多接受 4096 个匹配项以限制输出大小。

退出码：`0` 表示没有缺失的必需引用；`1` 表示至少一个引用缺失；`2` 表示输入格式错误或语法不受支持。错误只包含固定错误码。程序不联网、不启动进程，也不执行替换。

## 示例

```sh
python mcp_env_preflight.py < fixtures/example.json
```

准确输出：

```json
{"references":[{"name":"API_TOKEN","ordinal":1,"source":"declared"},{"name":"CACHE_DIR","ordinal":1,"source":"ambient"},{"name":"OPTIONAL","ordinal":2,"source":"fallback"}]}
```

退出码：`0`。更多准确示例见 [TESTING.zh-CN.md](TESTING.zh-CN.md)；英文版：[README.md](README.md)、[TESTING.md](TESTING.md)、[RESEARCH.md](RESEARCH.md)。

采用 MIT 许可证，见 [LICENSE](LICENSE)。

