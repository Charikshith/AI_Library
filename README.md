# AI Library

A living, curated catalogue of open-source AI tools & resources worth remembering — indexed, tagged, and dated. Built so I stop forgetting the good stuff.

🔎 **Friendly version:** https://charikshith.github.io/AI_Library/ — a searchable landing page, plus a **Notes** area for long-form study notes & cheatsheets.

> **This README is the source of truth for the tools catalogue.** The landing page (`index.html`) is *generated* from the table below — see [How it works](#how-it-works). Tools are added by telling Claude `add <tool>`; see [Adding a tool](#adding-a-tool). Long-form notes live as markdown under [`notes/`](notes/).

## Table of Contents

- [AI Agents & Skills](#ai-agents--skills)

<!-- TOOLS:START -->

## AI Agents & Skills

| Tool | Description | Tags | Added |
|------|-------------|------|-------|
| [Claude Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) | Modular, portable capabilities that extend Claude — a `SKILL.md` folder of instructions, scripts, and resources Claude loads automatically when a task is relevant. Works across Claude.ai, Claude Code, the Agent SDK, and the API. | `#claude` `#agents` `#anthropic` `#extensibility` | 2026-06-09 |

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
