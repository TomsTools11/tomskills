# Installing on each platform

Every skill here is a folder with a `SKILL.md` (YAML frontmatter with `name` and `description`, then instructions), plus optional `references/`, `scripts/`, and `assets/`. That format is the open Agent Skills standard, so the same folder works across platforms. Only the install step differs.

For personalized skills, build first so your values are filled in:

```bash
cp config/profile.example.yaml config/profile.yaml && $EDITOR config/profile.yaml
python3 scripts/build.py
```

`dist/` then contains:

| Path | Use it for |
|---|---|
| `dist/skills/<name>.zip` | Claude.ai, Claude Desktop, and the Skills API (one skill per zip, folder at the root) |
| `dist/plugins/<name>-<version>.zip` | Claude Cowork / Desktop plugin upload |
| `dist/flat/<name>/` | Copying into any agent's skills folder |

---

## Claude Code

**Option A: marketplace (recommended, updatable)**

```
/plugin marketplace add TomsTools11/tomskills
/plugin install <plugin>@tomskills
```

Plugins: `campaign-analyst`, `goal-disposition-import`, `research-company`, `account-ops-notion`. Run `/plugin marketplace update tomskills` to pull new versions.

Marketplace installs come straight from GitHub, so personalized skills still have their `{{PLACEHOLDER}}` tokens. They ask for the values on first run. To skip that, use Option B with a built copy.

**Option B: copy a skill folder**

```bash
# personal (all projects)
cp -r dist/flat/daily-account-brief ~/.claude/skills/
# or project-only
cp -r dist/flat/daily-account-brief .claude/skills/
```

## Claude.ai and Claude Desktop

1. **Settings → Capabilities**: make sure code execution and Skills are on.
2. **Skills → Upload skill**, then choose `dist/skills/<name>.zip`. A `.skill` file is the same zip with a different extension, so either works.
3. Connect what the skill needs (Notion, Close, Fathom, Slack, and so on) under **Settings → Connectors**.

## Claude Cowork plugins

Upload `dist/plugins/campaign-analyst-<version>.zip` or `dist/plugins/goal-disposition-import-<version>.zip` from the plugin manager. This is the same layout as the original plugin exports.

## Claude API and Agent SDK

- **Skills API:** upload a skill zip with the Skills endpoint, then reference its `skill_id` in the `container.skills` parameter of a Messages request that has code execution enabled. Check the current Anthropic docs for the beta header.
- **Agent SDK:** put skill folders in `.claude/skills/` (project) or `~/.claude/skills/` (user) and allow the `Skill` tool. The SDK discovers them the same way Claude Code does.

## Other agents (Codex, Cursor, Gemini CLI, Copilot, ...)

Many coding agents now read `SKILL.md` folders natively. Copy `dist/flat/<name>/` into the folder that tool scans for skills; its docs list the path. The community `skills` CLI can also install straight from this repo into many agents at once:

```bash
npx skills add TomsTools11/tomskills
```

Things to check on a non-Claude agent:

- Skills that call connectors (`notion-fetch`, Close `lead_search`, Fathom, Superhuman) need equivalent MCP servers in that agent, under similar tool names.
- `scripts/` need Python. `research-company` needs `pip install reportlab`, and `disposition-import` needs `pandas`.

## Chat tools without skill support (ChatGPT GPTs, Gemini Gems, Claude Projects)

Paste the body of `SKILL.md` (everything after the frontmatter) into the custom instructions. Upload the `references/` files as knowledge files. Scripts won't run automatically, so these tools are best for the reference-heavy skills like `right-pricing` and `disposition-import`.
