# Resources and References

The official references and skills mentioned throughout the guide, gathered here for convenience.

## Official documentation

- [Agent Skills — overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Extend Claude with Skills (Claude Code)](https://docs.claude.com/en/docs/claude-code/skills)
- [Using Agent Skills with the API](https://docs.claude.com/en/api/skills-guide)
- [Skills API reference (list / manage)](https://docs.claude.com/en/api/skills/list-skills)
- [Introducing Agent Skills (announcement)](https://www.anthropic.com/news/skills)
- [Equipping agents for the real world with Agent Skills (engineering blog)](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

> Implementation references called out in the guide: **Skills API Quickstart**, **Create Custom Skills**, and **Skills in the Agent SDK** (see the docs above).

## Skills referenced in the guide

- **`skill-creator`** — Interactive guide for creating new skills; available in Claude.ai via the plugin directory or as a download for Claude Code. Walks you through use-case definition, frontmatter generation, instruction writing, and validation.
- **`frontend-design`** — Create distinctive, production-grade frontend interfaces with high design quality (Category 1 example).
- **`sentry-code-review`** (from Sentry) — Analyzes and fixes detected bugs in GitHub PRs using Sentry's error-monitoring data via their MCP server (Category 3 example).
- **Office skills** (`docx`, `pptx`, `xlsx`, `ppt`) — Document/asset creation skills; referenced as examples of bundling validation scripts.

## Key facts to remember

- **Agent Skills is an open standard** — skills are intended to be portable across tools and platforms; use the `compatibility` field to note platform-specific requirements.
- **Skills in the API** require the **Code Execution Tool** beta (the secure runtime skills need).
- **Distribution surfaces:** Claude.ai (Settings > Capabilities > Skills), the Claude Code skills directory, and the API (`/v1/skills`, `container.skills`).
- **Org deployment:** admins can deploy skills workspace-wide with automatic updates and centralized management.

---

*This guide was converted from Anthropic's PDF, "The Complete Guide to Building Skills for Claude."*
