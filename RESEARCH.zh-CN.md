# Research notes

本项目刻意限定为离线占位符引用检查器，不是 MCP 配置验证器。VS Code 的一个议题讨论迁移到可移植 MCP 配置，描述将 `${env:NAME}` 迁移为 `${NAME}`，列出 `$VAR`、`${VAR}`、`${VAR:-default}` 等形式，并记录 Copilot 与 VS Code 客户端使用的环境来源存在差异。该议题及其关联状态为检查调用方声明的名称清单提供了背景，也说明本工具无法承诺客户端行为；它不能证明所有 MCP 客户端都遵循相同规则。

Microsoft Copilot SDK 的 MCP 文档描述了该 SDK 的本地/stdio 配置字段，包括 `command`、`args`、`env` 和工作目录。这只证明该 SDK 文档记录了这些配置字段，不代表所有客户端共用同一契约。

## 边界

本 CLI 接收配置文本和名称清单作为输入。它不会解析完整 MCP 配置 schema，不判断客户端会向服务器传递什么，不读取真实操作系统环境变量或验证秘密，也不会启动 MCP 服务器。`declared` 与 `ambient` 仅表示名称存在于输入列表；`fallback` 仅表示语法提供了 fallback（也包括空 fallback）。输出无法保证配置成功，也无法保证不同客户端的解释一致。

## 来源

- [VS Code issue #340161](https://github.com/microsoft/vscode/issues/340161)（迁移行为及明确记录的客户端差异；属于议题/报告语境）
- [Microsoft Copilot SDK MCP 功能文档](https://github.com/microsoft/copilot-sdk/blob/main/docs/features/mcp.md)（该 SDK 记录的本地/stdio 字段）

未将 [github/copilot-sdk#163](https://github.com/github/copilot-sdk/issues/163) 用作证据：它是用户报告和自动分诊内容，并非已验证或确认的根因结论。
