# Research notes

The project is intentionally a narrow offline reference checker, not an MCP configuration validator. A VS Code issue about migration to portable MCP configuration describes migration of `${env:NAME}` to `${NAME}`, lists `$VAR`, `${VAR}`, and `${VAR:-default}` among a portable format's forms, and documents differences in which environment source is used between Copilot and VS Code clients. This issue report and its linked status provide motivation for checking caller-declared source inventories, while also showing why this tool cannot promise client behavior. It does not establish universal behavior across MCP clients.

The Microsoft Copilot SDK MCP documentation describes local/stdio configuration fields including `command`, `args`, `env`, and a working directory. This is evidence of configuration fields in that SDK's documentation, not a common contract for every client.

## Limits

This CLI takes configuration text and name inventories as input. It does not parse an entire MCP configuration schema, determine what a client passes to a server, read actual OS environment values, validate secrets, or launch an MCP server. `declared` and `ambient` indicate only membership in the input lists. `fallback` indicates only syntactic fallback availability, including an empty fallback. Results cannot guarantee successful configuration or equivalent interpretation across clients.

## Sources

- [VS Code issue #340161](https://github.com/microsoft/vscode/issues/340161) (migration behavior and explicitly described client differences; issue/report context)
- [Microsoft Copilot SDK MCP feature documentation](https://github.com/microsoft/copilot-sdk/blob/main/docs/features/mcp.md) (documented local/stdio fields for that SDK)

The report [github/copilot-sdk#163](https://github.com/github/copilot-sdk/issues/163) was not used as evidence: it is a user report and automated triage, not a verified or confirmed root-cause statement.
