# mcp-env-preflight

A small offline Python 3.11+ CLI that checks environment placeholder references in caller-supplied MCP configuration text. It accepts only explicitly supplied names, reads no process environment, and never expands or substitutes values.

## Input and behavior

Send one strict UTF-8 JSON object on stdin, at most 256 KiB. The exact top-level keys are `values`, `declared_names`, and `ambient_names`. `values` is a list of 1–64 strings, each at most 4096 Unicode code points. Each names array has at most 128 unique ASCII names matching `[A-Za-z_][A-Za-z0-9_]{0,127}`.

The recognized subset is `$NAME`, `${NAME}`, and `${NAME:-fallback}`. A fallback can be empty and ends at the next `}`; it cannot nest another `${...}`. The tool scans text only; it is not a complete shell, dotenv, JSON, or MCP-client parser. Unsupported or malformed braced placeholders are rejected. A bare `$` not followed by a valid name remains ordinary text.

For each recognized occurrence, output gives its 1-based `ordinal`, variable `name`, and `source`: `declared` takes precedence over `ambient`; `fallback` is used only when the name appears in neither list and the syntax has a fallback; otherwise it is `missing`. Values, fallback contents, paths, and OS environment data are never emitted. Output order follows input value order and position within each string. At most 4096 occurrences are accepted to keep output bounded.

Exit codes: `0` no required reference is missing; `1` at least one reference is missing; `2` malformed/unsupported input. Errors contain a fixed code only. The program makes no network requests, starts no process, and performs no substitution.

## Example

```sh
python mcp_env_preflight.py < fixtures/example.json
```

Exact output:

```json
{"references":[{"name":"API_TOKEN","ordinal":1,"source":"declared"},{"name":"CACHE_DIR","ordinal":1,"source":"ambient"},{"name":"OPTIONAL","ordinal":2,"source":"fallback"}]}
```

Exit code: `0`. More exact cases are in [TESTING.md](TESTING.md); Chinese: [README.zh-CN.md](README.zh-CN.md), [TESTING.zh-CN.md](TESTING.zh-CN.md), [RESEARCH.zh-CN.md](RESEARCH.zh-CN.md).

MIT licensed. See [LICENSE](LICENSE).

