# Claude Instructions

This project includes Claude-compatible local skills in `.claude/skills`.
When a task touches Ant Design X chat UI, streaming providers, Markdown
rendering, or agent-rendered cards, load the relevant skill before editing.

## Skills

- `x-components`: `@ant-design/x` UI components such as Bubble, Sender,
  Conversations, Prompts, ThoughtChain, Sources, and XProvider.
- `use-x-chat`: `useXChat` integration, message lifecycle, request state,
  cancellation, errors, and multi-session handling.
- `x-chat-provider`: custom provider integration for streaming chat APIs.
- `x-markdown`: Markdown rendering, custom component mapping, code blocks,
  Mermaid, and streamed rich text.
- `x-card`: `@ant-design/x-card` dynamic UI, catalog, actions, and data binding.

Keep `.agents/skills` as the shared Codex-compatible source of truth and keep
Claude behavior aligned with those skill boundaries.
