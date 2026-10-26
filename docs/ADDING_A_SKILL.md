# Adding or updating a skill

## New standalone skill

1. Copy the template: `cp -r templates/skill-template skills/<your-skill-name>`
2. Edit `SKILL.md`:
   - `name`: lowercase letters, digits, and hyphens. It must match the folder name (max 64 chars).
   - `description`: what the skill does and the phrases that should trigger it (max 1024 chars). Claude reads only this when deciding whether to load the skill, so name the trigger phrases.
   - Body: the workflow. Keep it under ~500 lines and move long material into `references/`.
3. Add an entry to `.claude-plugin/marketplace.json`, either in an existing group or as a new plugin with `"source": "./"`, `"strict": false`, and `"skills": ["./skills/<name>"]`.
4. Add a row to the catalog table in `README.md`.
5. Run `python3 scripts/build.py --check`.

## Importing a skill exported from Claude (`.skill` / `.zip`)

```bash
unzip ~/Downloads/my-skill.skill -d skills/        # creates skills/my-skill/
unzip ~/Downloads/My_plugin-1.0.0.zip -d plugins/my-plugin/
```

Then work through the checklist below before committing. **This repo is public.**

## Pre-commit checklist for public sharing

- [ ] No real client or agency names. Use fictional ones (Harbor Point, Lindqvist, Northwind, Lakeside, ...).
- [ ] No colleague names. Use a role ("the account manager", "your compliance contact").
- [ ] No emails, Slack channel IDs, Notion database/template IDs, or API keys. Use `{{PLACEHOLDER}}` tokens.
- [ ] Every new placeholder is declared in `config/profile.example.yaml` (the build fails otherwise) and explained in the skill's `<!-- config:start -->` block.
- [ ] Run the scan:

```bash
grep -rnEi '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}|sk-[a-z0-9]|api[_-]?key' skills plugins
```

## Personalized skills

Placeholders look like `{{USER_NAME}}`. Put the setup notes between markers so personalized builds can drop them:

```markdown
<!-- config:start -->
## Configuration
...table of placeholders...
<!-- config:end -->
```

`scripts/build.py` replaces only keys declared in `config/profile.example.yaml`. Other `{{...}}` tokens, such as report-template slots like `{{CLIENT_NAME}}`, are left alone.

## Versioning

- Plugins: bump `version` in `plugins/<name>/.claude-plugin/plugin.json` and the matching entry in `marketplace.json`.
- Release: `git tag v1.2.0 && git push origin v1.2.0`. CI attaches fresh zips to the GitHub Release.
