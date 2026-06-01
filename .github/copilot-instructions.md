# GitHub Copilot Instructions

This repository uses local AI-agent skills. Copilot does not execute Codex
skills directly, but suggestions should follow the same boundaries.

## Relevant Skills

- `x-components`: apply for `@ant-design/x` UI component work.
- `use-x-chat`: apply for `useXChat`, chat message state, cancellation, errors,
  and multi-session behavior.
- `x-chat-provider`: apply for custom streaming provider adapters.
- `x-markdown`: apply for Markdown, code, Mermaid, and streamed rich content in
  chat output.
- `x-card`: apply for dynamic `@ant-design/x-card` agent UI rendering.

## Repository Guidance

- Preserve the existing FastAPI service/router/schema structure.
- Preserve the existing React, TypeScript, Ant Design X, and Vite conventions in
  `web/`.
- Prefer focused edits over broad rewrites.
- Keep secrets and local runtime files out of source control.
- Validate changed backend files with Python syntax or focused tests, and
  validate changed frontend files with the existing lint/build commands when
  practical.
