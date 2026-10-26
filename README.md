# tomskills

Claude skills and plugins I use every day for insurance performance marketing, GOAL Platform account management, and B2B research. Each one is a plain `SKILL.md` folder, so it works in Claude Code, Claude.ai, Claude Desktop/Cowork, and the Claude API. It also works in any other agent that reads the open Agent Skills format.

## Catalog

| Name | Type | What it does | Needs |
|---|---|---|---|
| [campaign-analyst](plugins/campaign-analyst) | Plugin: 3 skills, 2 commands, 2 agents | Four-layer GOAL campaign diagnosis, RightPricing source modifiers, and client-facing HTML account review reports | GOAL CSV exports. Optional: Close, Fathom, email, web search |
| [goal-disposition-import](plugins/goal-disposition-import) | Plugin: 1 skill, 1 command | Maps raw CRM disposition exports to GOAL's Conversion Bulk Import CSV, flagging anything ambiguous | Python + pandas |
| [research-company](skills/research-company) | Skill | Researches a company from its URL and outputs a styled PDF account report | Web search/fetch, Python + `reportlab` |
| [daily-account-brief](skills/daily-account-brief) | Skill, personalized | Weekday morning brief in Notion: confirms finished tasks, scans email/Fathom/Slack, creates tasks, builds the Daily Brief note | Notion, Superhuman, Fathom, Slack, Close |
| [account-recent-updates](skills/account-recent-updates) | Skill, personalized | Writes or refreshes the "Recent Updates" status callout on a Notion account page | Notion, Close, Superhuman, Fathom |

**Personalized** skills contain `{{PLACEHOLDER}}` tokens (your name, emails, Notion database IDs, Slack channel). See [Personalizing](#personalizing). If you don't fill them, the skill asks for the values the first time it runs.

## Install

The fastest route for each platform is below. [docs/INSTALL.md](docs/INSTALL.md) has every option, including the API and non-Claude agents.

**Claude Code** (installs straight from this repo and stays updatable):

```
/plugin marketplace add TomsTools11/tomskills
/plugin install campaign-analyst@tomskills
/plugin install goal-disposition-import@tomskills
/plugin install research-company@tomskills
/plugin install account-ops-notion@tomskills
```

**Claude.ai / Claude Desktop / Cowork** (upload a zip):

1. Download the zips from the [latest release](https://github.com/TomsTools11/tomskills/releases/latest), or build them yourself with `python3 scripts/build.py`.
2. Skills: **Settings → Capabilities → Skills → Upload skill**, then pick a file from `dist/skills/`.
3. Plugins (Cowork): upload a file from `dist/plugins/`.

## Personalizing

```bash
cp config/profile.example.yaml config/profile.yaml   # git-ignored
# fill in your values
python3 scripts/build.py
```

`dist/` now holds copies with your values filled in (and the setup notes removed), ready to upload. Files in git stay generic, so your IDs and emails never get committed.

## Repo layout

```
.claude-plugin/marketplace.json   Claude Code marketplace: lists every installable plugin
plugins/<name>/                   Full plugins (skills + commands + agents + .claude-plugin/plugin.json)
skills/<name>/                    Standalone skills (SKILL.md + optional references/, scripts/, assets/)
config/profile.example.yaml       Placeholder values for personalized skills
scripts/build.py                  Validate, personalize, and package everything into dist/
templates/skill-template/         Starting point for a new skill
docs/                             Install guide for each platform, how to add a skill
```

## Adding a skill

See [docs/ADDING_A_SKILL.md](docs/ADDING_A_SKILL.md). In short: drop the folder into `skills/` (or a plugin into `plugins/`), add it to `marketplace.json`, run `python3 scripts/build.py --check`, and open a PR. CI runs the same check.

## Releasing

Push a tag like `v1.1.0`. The release workflow builds generic (unpersonalized) zips and attaches them to a GitHub Release, which is what other people download.

## A note on content

These skills encode GOAL Platform workflows and my own bidding and reporting rules. Client names and examples are fictional. Account-specific values are placeholders. Test on your own data before relying on the output.
