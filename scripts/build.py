#!/usr/bin/env python3
"""Validate, personalize, and package the skills and plugins in this repo.

Usage:
    python3 scripts/build.py            # validate + build dist/ (uses config/profile.yaml if present)
    python3 scripts/build.py --check    # validate only, no output (what CI runs)
    python3 scripts/build.py --profile path/to/profile.yaml

Outputs (dist/ is git-ignored):
    dist/skills/<name>.zip            upload to Claude.ai / Claude Desktop (Settings > Capabilities > Skills)
    dist/plugins/<name>-<version>.zip  upload to Claude Cowork / Claude Desktop as a plugin
    dist/flat/<name>/                  plain SKILL.md folders for other agents (Cursor, Codex, Gemini CLI, ...)

Personalization: every {{KEY}} declared in config/profile.example.yaml is replaced
with its value from the profile. Other {{...}} tokens (e.g. report-template slots like
{{CLIENT_NAME}}) are left alone. When every placeholder in a SKILL.md is filled, its
<!-- config:start --> ... <!-- config:end --> block is dropped from the built copy.
Only the built copies in dist/ are personalized; the files in git stay generic.

Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
DEFAULT_PROFILE = ROOT / "config" / "profile.yaml"
EXAMPLE_PROFILE = ROOT / "config" / "profile.example.yaml"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
CONFIG_BLOCK_RE = re.compile(r"<!-- config:start -->.*?<!-- config:end -->\n*", re.S)
TEXT_SUFFIXES = {".md", ".txt", ".py", ".html", ".json", ".yaml", ".yml", ".csv", ".js", ".css", ".sh"}
MAX_NAME = 64
MAX_DESCRIPTION = 1024

errors: list[str] = []
KNOWN_KEYS: set[str] = set()
warnings: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def load_profile(path: Path | None, keep_empty: bool = False) -> dict[str, str]:
    """Read a flat `KEY: value` YAML file (no nesting, no lists)."""
    if not path or not path.exists():
        return {}
    values = {}
    for n, line in enumerate(path.read_text().splitlines(), 1):
        line = line.split(" #", 1)[0].rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"{rel(path)}:{n}: expected `KEY: value`")
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value or keep_empty:
            values[key.strip()] = value
    return values


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return top-level scalar keys from YAML frontmatter, or None if missing."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    key = None
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2)
        elif key and line.startswith((" ", "\t", "-")):
            fields[key] += " " + line.strip()
    for k, v in fields.items():
        v = v.strip()
        if v in {"|", ">", "|-", ">-"}:
            v = ""
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        fields[k] = v.strip()
    return fields


def find_skills() -> list[Path]:
    return sorted(
        list((ROOT / "skills").glob("*/SKILL.md"))
        + list((ROOT / "plugins").glob("*/skills/*/SKILL.md"))
    )


def validate_skill(skill_md: Path) -> dict[str, str] | None:
    fm = parse_frontmatter(skill_md.read_text())
    where = rel(skill_md)
    if fm is None:
        errors.append(f"{where}: missing YAML frontmatter (--- name/description ---)")
        return None
    name, desc = fm.get("name", ""), fm.get("description", "")
    folder = skill_md.parent.name
    if not name:
        errors.append(f"{where}: frontmatter has no `name`")
    elif name != folder:
        errors.append(f"{where}: name `{name}` must match its folder `{folder}`")
    elif not NAME_RE.match(name) or len(name) > MAX_NAME:
        errors.append(f"{where}: name `{name}` must be lowercase letters, digits, and hyphens (max {MAX_NAME})")
    if not desc:
        errors.append(f"{where}: frontmatter has no `description`")
    elif len(desc) > MAX_DESCRIPTION:
        errors.append(f"{where}: description is {len(desc)} chars (max {MAX_DESCRIPTION})")
    return fm


def validate_plugins() -> list[dict]:
    plugins = []
    for manifest in sorted((ROOT / "plugins").glob("*/.claude-plugin/plugin.json")):
        try:
            data = json.loads(manifest.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{rel(manifest)}: invalid JSON ({e})")
            continue
        folder = manifest.parent.parent.name
        if data.get("name") != folder:
            errors.append(f"{rel(manifest)}: name `{data.get('name')}` must match folder `{folder}`")
        if not data.get("version"):
            warnings.append(f"{rel(manifest)}: no `version`")
        data["_dir"] = manifest.parent.parent
        plugins.append(data)
    return plugins


def validate_marketplace(plugins: list[dict]) -> None:
    path = ROOT / ".claude-plugin" / "marketplace.json"
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"{rel(path)}: {e}")
        return
    listed = set()
    for entry in data.get("plugins", []):
        name = entry.get("name", "?")
        listed.add(name)
        src = ROOT / entry.get("source", "")
        if not src.is_dir():
            errors.append(f"marketplace: `{name}` source `{entry.get('source')}` does not exist")
        for skill in entry.get("skills", []):
            if not (src / skill / "SKILL.md").exists():
                errors.append(f"marketplace: `{name}` lists missing skill `{skill}`")
    for p in plugins:
        if p["name"] not in listed:
            warnings.append(f"marketplace: plugin `{p['name']}` is not listed in marketplace.json")
    for skill_md in (ROOT / "skills").glob("*/SKILL.md"):
        ref = f"./skills/{skill_md.parent.name}"
        if not any(ref in e.get("skills", []) for e in data.get("plugins", [])):
            warnings.append(f"marketplace: standalone skill `{skill_md.parent.name}` is not in any marketplace entry")


def render(text: str, profile: dict[str, str]) -> tuple[str, set[str]]:
    missing = set()

    def repl(m: re.Match) -> str:
        key = m.group(1)
        if key not in KNOWN_KEYS:
            return m.group(0)
        if key in profile:
            return profile[key]
        missing.add(key)
        return m.group(0)

    out = PLACEHOLDER_RE.sub(repl, text)
    if not missing:
        out = CONFIG_BLOCK_RE.sub("", out)
    return out, missing


def copy_rendered(src: Path, dst: Path, profile: dict[str, str]) -> set[str]:
    missing: set[str] = set()
    for f in sorted(src.rglob("*")):
        if f.is_dir() or "__pycache__" in f.parts or f.name == ".DS_Store":
            continue
        target = dst / f.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        if f.suffix in TEXT_SUFFIXES:
            text, miss = render(f.read_text(), profile)
            missing |= miss
            target.write_text(text)
        else:
            shutil.copy2(f, target)
    return missing


def zip_dir(src: Path, zip_path: Path, prefix: str) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            if f.is_file():
                z.write(f, str(Path(prefix) / f.relative_to(src)))


def build(profile: dict[str, str], plugins: list[dict]) -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    stage = DIST / "flat"

    for skill_md in find_skills():
        name = skill_md.parent.name
        out = stage / name
        missing = copy_rendered(skill_md.parent, out, profile)
        zip_dir(out, DIST / "skills" / f"{name}.zip", name)
        if missing:
            warnings.append(f"{name}: unfilled placeholders {sorted(missing)} (skill will ask for them at run time)")

    for p in plugins:
        tmp = DIST / ".tmp" / p["name"]
        copy_rendered(p["_dir"], tmp, profile)
        zip_dir(tmp, DIST / "plugins" / f"{p['name']}-{p.get('version', '0.0.0')}.zip", "")
    shutil.rmtree(DIST / ".tmp", ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="validate only; do not write dist/")
    ap.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="flat YAML of placeholder values")
    args = ap.parse_args()

    skills = find_skills()
    for s in skills:
        validate_skill(s)
    plugins = validate_plugins()
    validate_marketplace(plugins)
    global KNOWN_KEYS
    KNOWN_KEYS = set(load_profile(EXAMPLE_PROFILE, keep_empty=True))
    if not KNOWN_KEYS:
        errors.append(f"{rel(EXAMPLE_PROFILE)}: missing or empty")
    for s in skills:
        # Personalized skills (those with a config block) may only use declared profile keys.
        # Elsewhere {{...}} can be legitimate content, e.g. a prompt-template variable.
        if "<!-- config:start -->" not in s.read_text():
            continue
        for key in set(PLACEHOLDER_RE.findall(s.read_text())) - KNOWN_KEYS:
            errors.append(f"{rel(s)}: placeholder {{{{{key}}}}} is not declared in {rel(EXAMPLE_PROFILE)}")
    profile = {} if args.check else load_profile(args.profile)

    if not errors and not args.check:
        build(profile, plugins)

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    if errors:
        return 1
    print(f"ok: {len(skills)} skills, {len(plugins)} plugins validated", end="")
    if args.check:
        print()
    else:
        used = f", personalized from {rel(args.profile)}" if profile else ""
        print(f"; built to dist/{used}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
