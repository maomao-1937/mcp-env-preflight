# 测试与准确示例

运行标准库测试：

```sh
python -m unittest discover -s tests -v
```

## 合成样例

在项目根目录执行：

```sh
python mcp_env_preflight.py < fixtures/example.json
```

准确 stdout：

```json
{"references":[{"name":"API_TOKEN","ordinal":1,"source":"declared"},{"name":"CACHE_DIR","ordinal":1,"source":"ambient"},{"name":"OPTIONAL","ordinal":2,"source":"fallback"}]}
```

退出码：`0`。

当必需引用不在任一名称清单中时，以下输入：

```json
{"values":["${MISSING}"],"declared_names":[],"ambient_names":[]}
```

准确输出：

```json
{"references":[{"name":"MISSING","ordinal":1,"source":"missing"}]}
```

退出码：`1`。

UTF-8/JSON 错误、重复 JSON 键、不支持的花括号语法、形状错误或资源限制超限时，返回退出码 `2` 和固定错误对象。例如输入 `{` 的准确输出是 `{"error":"invalid_json"}`。配置内容和 fallback 不会被回显。证据边界见 [RESEARCH.zh-CN.md](RESEARCH.zh-CN.md)。英文版：[TESTING.md](TESTING.md)。

