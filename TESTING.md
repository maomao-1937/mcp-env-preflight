# Testing and exact examples

Run the standard-library suite:

```sh
python -m unittest discover -s tests -v
```

## Synthetic fixture

From the project root:

```sh
python mcp_env_preflight.py < fixtures/example.json
```

Exact stdout:

```json
{"references":[{"name":"API_TOKEN","ordinal":1,"source":"declared"},{"name":"CACHE_DIR","ordinal":1,"source":"ambient"},{"name":"OPTIONAL","ordinal":2,"source":"fallback"}]}
```

Exit code: `0`.

For a required reference absent from both inventories, this input:

```json
{"values":["${MISSING}"],"declared_names":[],"ambient_names":[]}
```

produces exactly:

```json
{"references":[{"name":"MISSING","ordinal":1,"source":"missing"}]}
```

Exit code: `1`.

Malformed UTF-8/JSON, duplicate JSON keys, unsupported braced syntax, invalid shape, or resource-limit violations return exit `2` and a fixed error object. For example, input `{` produces exactly `{"error":"invalid_json"}`. Configuration contents and fallbacks are never echoed. See [RESEARCH.md](RESEARCH.md) for evidence boundaries. Chinese: [TESTING.zh-CN.md](TESTING.zh-CN.md).

