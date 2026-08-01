# AI Library

A living, curated catalogue of open-source AI tools & resources worth remembering — indexed, tagged, and dated. Built so I stop forgetting the good stuff.

🔎 **Friendly version:** https://charikshith.github.io/AI_Library/ — a searchable landing page, plus a **Notes** area for long-form study notes & cheatsheets.

> **This README is the source of truth for the tools catalogue.** The landing page (`index.html`) is *generated* from the table below — see [Maintenance](#maintenance).

## Table of Contents

- [AI SDE Skills](#ai-sde-skills)
- [AI Guides](#ai-guides)
- [Misc](#misc)
- [Text to Speech](#text-to-speech)

<!-- TOOLS:START -->

## AI SDE Skills

### Agent Platforms

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [pi_agent_rust](https://github.com/Dicklesworthstone/pi_agent_rust) | High-performance AI coding agent CLI written in Rust with zero unsafe code. | `#agent-platform` `#cli` `#rust` `#performance` | 2026-08-01 |
| [Pi](https://github.com/earendil-works/pi) | AI agent toolkit: unified LLM API, agent loop, TUI, and coding agent CLI. 64k stars. | `#agent-toolkit` `#llm-api` `#agent-loop` `#cli` | 2026-06-21 |
| [Paperclip](https://github.com/paperclipai/paperclip) | An open-source app for managing a team of AI agents at work. Bring your own agents, assign goals, and track work and costs from one dashboard. 71k stars. | `#agent-orchestration` `#dashboard` `#management` `#open-source` | 2026-06-21 |
| [Goose](https://github.com/aaif-goose/goose) | An open-source, extensible AI agent that goes beyond code suggestions — install, execute, edit, and test with any LLM. Works with 15+ providers. 50k stars. | `#agent-platform` `#extensible` `#multi-llm` `#open-source` | 2026-06-21 |

### Agent Configs

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [gstack](https://github.com/garrytan/gstack) | Garry Tan's exact Claude Code setup — 23 opinionated tools that serve as CEO, Designer, Eng Manager, Release Manager, Doc Engineer, and QA. 112k stars. | `#agent-framework` `#workflow` `#opinionated` `#claude-code` | 2026-06-21 |
| [Superpowers](https://github.com/obra/superpowers) | An agentic skills framework and software development methodology for Claude Code. Structured skills, planning, and execution flow. | `#skills-framework` `#methodology` `#planning` `#claude-code` | 2026-06-21 |
| [ECC](https://github.com/affaan-m/ecc) | An agent harness performance optimization system — skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor, and beyond. | `#agent-harness` `#performance` `#security` `#claude-code` | 2026-06-21 |

### Agent Utilities

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [code-review-graph](https://github.com/tirth8205/code-review-graph) | Local-first code intelligence graph for MCP and CLI — builds a persistent map of your codebase so AI coding tools read only what matters, with benchmarked context reductions on reviews and large-repo workflows. | `#code-intelligence` `#knowledge-graph` `#mcp` `#context-reduction` | 2026-08-01 |
| [pi-intercom](https://github.com/nicobailon/pi-intercom) | Inter-session communication extension for the pi coding agent — lets sessions talk to each other so context carries across. | `#inter-session` `#persistent-memory` `#agent-plugin` `#pi` | 2026-08-01 |
| [claude-mem](https://github.com/thedotmack/claude-mem) | Persistent context across sessions for every agent — captures everything your agent does, compresses it with AI, and injects relevant context back into future sessions. Works with Claude Code, Codex, Gemini, Copilot, and more. | `#persistent-memory` `#context-injection` `#session-compression` `#agent-plugin` | 2026-07-04 |
| [Headroom](https://github.com/chopratejas/headroom) | Compress tool outputs, logs, files, and RAG chunks before they reach the LLM. 60-95% fewer tokens, same answers. Library, proxy, MCP server. | `#context-compression` `#token-optimization` `#proxy` `#agent-plugin` | 2026-06-21 |
| [Ponytail](https://github.com/DietrichGebert/ponytail) | Makes your AI agent think like the laziest senior dev in the room. ~54% less code, ~20% cheaper, ~27% faster — 100% safety. Plugs into 14 agents (Claude Code, Codex, Cursor, Copilot, and more). | `#yagni` `#code-reduction` `#lazy-dev` `#agent-plugin` | 2026-06-20 |

### Security Skills

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [VibeSec-Skill](https://github.com/BehiSecc/VibeSec-Skill) | A Claude Code skill that helps Claude write secure code and prevent common vulnerabilities. Covers 60-70% of common vulnerability classes. | `#security` `#vulnerable-code` `#claude-code` `#skill` | 2026-07-04 |

## AI Guides

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch) | A project-based curriculum covering the full stack of AI engineering — from environment setup and tooling through to shipping production systems. 388 skills and 99 prompts across phased modules. | `#ai-engineering` `#full-stack` `#curriculum` `#hands-on` | 2026-06-21 |
| [Learn Harness Engineering](https://github.com/walkinglabs/learn-harness-engineering) | A project-based open-source course on building the environment, state management, verification, and control that make AI coding agents work reliably — 12 lectures + 6 hands-on projects. | `#harness-engineering` `#agent-training` `#course` `#hands-on` | 2026-06-11 |
| [Building Claude Skills — The Complete Guide](notes/building-claude-skills/html/index.html) | Anthropic's complete guide to building Skills for Claude — `SKILL.md` structure & YAML frontmatter, planning, testing, distribution, and proven patterns. Converted in full from the official PDF and readable in-library. | `#skill-authoring` `#anthropic` `#official-guide` `#claude` | 2026-06-11 |

## Text to Speech

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [Kokoro](https://github.com/hexgrad/kokoro) | Inference library for Kokoro-82M, an open-weight 82M-parameter TTS model with quality comparable to far larger models — Apache-licensed, fast and cheap to deploy. | `#tts` `#speech-synthesis` `#open-source` `#lightweight` | 2026-08-01 |
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Open-source TTS model series from the Qwen team — stable, expressive, streaming speech generation, free-form voice design, and voice cloning. | `#tts` `#speech-synthesis` `#voice-cloning` `#open-source` | 2026-08-01 |
| [Audio8_TTS](https://github.com/Audio8-AI/Audio8_TTS) | State-of-the-art-class text-to-speech at compact scale — a small-footprint TTS model with strong quality. | `#tts` `#audio` `#speech-synthesis` `#open-source` | 2026-08-01 |

<!-- TOOLS:END -->

## Maintenance

- Add tools by saying `add <tool name or URL>` to Claude — full curation rules live in [`CLAUDE.md`](CLAUDE.md).
- Run `python scripts/build.py` to regenerate `index.html` and `notes.html` from this README and [`notes/`](notes/).
- The generated HTML is committed and served by **GitHub Pages** from the repo root. No server, no framework.
