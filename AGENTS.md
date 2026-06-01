# Agent Instructions

This repository keeps reusable AI-agent skills in `.agents/skills`, following the
Codex skills layout documented by OpenAI. Each skill directory contains a
`SKILL.md` file with frontmatter and optional `reference/` material.

## Skill Usage

- Use `.agents/skills` as the canonical shared skill location for Codex.
- Use `.claude/skills` for Claude-compatible local skills.
- Use `.codex/skills` only as the legacy Codex mirror already present in this
  repository.
- GitHub Copilot should follow `.github/copilot-instructions.md`, which points
  to the same skill names and development boundaries.

## Available Project Skills

- `x-components`: use when building or modifying `@ant-design/x` conversation UI.
- `use-x-chat`: use when working with `useXChat`, message state, request state,
  cancellation, or multi-session chat behavior.
- `x-chat-provider`: use when adapting a streaming backend into an
  `@ant-design/x-sdk` chat provider.
- `x-markdown`: use when rendering Markdown, code, Mermaid, or streamed rich
  content inside chat bubbles.
- `x-card`: use when creating dynamic `@ant-design/x-card` UI for agent output.

## Project Guardrails

- Keep backend/provider changes routed through the existing service and schema
  layers.
- Keep frontend chat changes consistent with the current React, TypeScript,
  Ant Design X, and Vite structure.
- Prefer narrow, behavior-preserving edits unless the user explicitly asks for a
  redesign or architecture change.
- Before finishing implementation work, run the smallest meaningful validation
  available for the files changed.
