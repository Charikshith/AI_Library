# AI Library

A living, curated catalogue of open-source AI tools & resources worth remembering — indexed, tagged, and dated. Built so I stop forgetting the good stuff.

🔎 **Friendly version:** https://charikshith.github.io/AI_Library/ — a searchable landing page, plus a **Notes** area for long-form study notes & cheatsheets.

> **This README is the source of truth for the tools catalogue.** The landing page (`index.html`) is *generated* from the table below — see [How it works](#how-it-works). Tools are added by telling Claude `add <tool>`; see [Adding a tool](#adding-a-tool). Long-form notes live as markdown under [`notes/`](notes/).

## Table of Contents

- [AI SDE Skills](#ai-sde-skills)
- [AI Guides](#ai-guides)

<!-- TOOLS:START -->

## AI SDE Skills

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [Fable Mode](https://github.com/Poorna-Repos/opus-fable-mode) | A behavioral governor and re-injection hook that makes Claude Opus 4.8 behave like the suspended Claude Fable 5 in Claude Code. Includes a leak-test harness measured from real logs. | `#claude` `#agents` `#skills` `#llm` | 2026-06-20 |
| [Ponytail](https://github.com/DietrichGebert/ponytail) | Makes your AI agent think like the laziest senior dev in the room. ~54% less code, ~20% cheaper, ~27% faster — 100% safety. Plugs into 14 agents (Claude Code, Codex, Cursor, Copilot, and more). | `#agents` `#yagni` `#claude` `#skills` `#llm` | 2026-06-20 |

## AI Guides

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [Learn Harness Engineering](https://github.com/walkinglabs/learn-harness-engineering) | A project-based open-source course on building the environment, state management, verification, and control that make AI coding agents work reliably — 12 lectures + 6 hands-on projects. | `#agents` `#harness` `#llm` `#course` | 2026-06-11 |
| [Building Claude Skills — The Complete Guide](notes/building-claude-skills/html/index.html) | Anthropic's complete guide to building Skills for Claude — `SKILL.md` structure & YAML frontmatter, planning, testing, distribution, and proven patterns. Converted in full from the official PDF and readable in-library. | `#claude` `#skills` `#anthropic` `#guide` | 2026-06-11 |

<!-- TOOLS:END -->

## How it works

- The catalogue data lives **only** in the table(s) between the `<!-- TOOLS:START -->` and `<!-- TOOLS:END -->` markers above.
- Running `python scripts/build.py` parses those tables and regenerates `index.html` (the searchable, filterable landing page) and `notes.html`.
- Long-form **notes** live as markdown under `notes/<subject>/markdown/` (organised Subject → Chapter); the same build step generates that subject's pages into `notes/<subject>/html/` — a themed, syntax-highlighted page per chapter. Source (`markdown/`) and output (`html/`) sit together per subject but in separate subfolders.
- The generated HTML is committed and served by **GitHub Pages** from the repo root at the link above. No server, no framework, no build pipeline beyond that one script.

## Adding a tool

Just tell Claude: **`add <tool name or URL>`**. Claude will:

1. Check it isn't already listed (dedupe).
2. Write a concise, neutral one-line description.
3. Pick an existing category — or create a new one (and add it to the Table of Contents).
4. Add lowercase `#tags`, reusing existing tags where possible.
5. Stamp today's date and insert the row **newest-first** in its category.
6. Run the build and commit `README.md` + `index.html` together.

Conventions: categories are `##` headings, ordered alphabetically in the ToC; one-offs that don't fit a category yet go under **Misc** until ~3 accumulate into their own category.
