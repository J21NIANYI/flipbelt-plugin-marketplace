# Tool Policy

| Expert | FlipBelt MCP | General web | Research | Race web | Weather |
|---|---|---|---|---|---|
| Foundation | direct, read-only | no | no | no | no |
| Product | via Foundation protocol | discovery only, not facts | no | no | no |
| Sizing | via Foundation protocol | no | only when explicitly needed, not product facts | no | no |
| Material | via Foundation protocol | controlled | standards/papers | no | contextual only |
| Running | via Foundation protocol | controlled | when relevant | official-first | yes |
| Review | via relevant expert | limited verification | via expert | via Running | no |
| Brand | via Foundation protocol | limited context, not brand facts | no | no | no |
| Chief | limited direct access | conditional | via expert | via Running | via Running |

Skill 文本不授予运行时权限。工具不可用时降级为 Unknown，而不是模拟调用结果。所有 MCP 操作保持只读。
