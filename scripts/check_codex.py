#!/usr/bin/env python3
"""Check package discovery, relocatable references and migration invariants."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote

from build_codex import ROOT, frontmatter, outputs


def main():
    expected = outputs()
    for relative, content in expected.items():
        assert (ROOT / relative).read_text() == content, f"Stale: {relative}"
    catalog = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    assert len(catalog["plugins"]) == 3
    skill_count = role_count = 0
    with tempfile.TemporaryDirectory(prefix="codex-package-check-") as scratch:
        for entry in catalog["plugins"]:
            source = ROOT / entry["source"]["path"]
            package = Path(scratch) / entry["name"]
            shutil.copytree(source, package)
            manifest = json.loads((package / "plugin.json").read_text())
            assert manifest["name"] == entry["name"]
            assert manifest["$schema"].endswith("/1.0.0/plugin.schema.json")
            extension = manifest["extensions"]["com.openai"]
            if "onboardingSkill" in extension:
                assert (package / extension["onboardingSkill"]).is_file()
            for path in package.rglob("*.md"):
                content = path.read_text()
                assert not re.search(r"CLAUDE_PLUGIN_ROOT|CLAUDE\.md|AskUserQuestion|TaskCreate|"
                                     r"TaskUpdate|TaskList|ToolSearch|subagent_type=|\bSkill\(|\bAgent\(", content), path
                for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
                    if "://" in link or link.startswith("#") or "<" in link:
                        continue
                    target = (path.parent / unquote(link.split("#")[0])).resolve()
                    assert target.is_relative_to(package), f"Escapes package: {path}: {link}"
                    assert target.exists(), f"Broken link: {path}: {link}"
                if path.name == "SKILL.md":
                    skill_count += 1
                    fields, _ = frontmatter(content)
                    assert fields["name"] == path.parent.name
                    assert json.loads(fields["description"])
                    assert set(fields) == {"name", "description"}
                    assert "allow_implicit_invocation: false" in (path.parent / "agents/openai.yaml").read_text()
                elif path.parent.name == "agents":
                    role_count += 1
            for role in re.findall(r'role="([a-z-]+)"',
                    "\n".join(p.read_text() for p in package.rglob("SKILL.md"))):
                assert (package / "agents" / (role + ".md")).exists(), role
            for skill in re.findall(r'run_skill\(skill="[^:"]+:([a-z-]+)"\)',
                    "\n".join(p.read_text() for p in package.rglob("SKILL.md"))):
                assert (package / "skills" / skill / "SKILL.md").exists(), skill
    assert skill_count == 11 and role_count == 7, (skill_count, role_count)
    # Exercise the real CLI parser without installing or changing user config.
    if shutil.which("codex"):
        result = subprocess.run([
            "codex", "-c", 'marketplaces.k1nak0.source_type="local"',
            "-c", "marketplaces.k1nak0.source=" + json.dumps(str(ROOT)),
            "plugin", "list", "--marketplace", "k1nak0", "--available", "--json",
        ], text=True, capture_output=True, check=True)
        available = json.loads(result.stdout)["available"]
        assert {p["name"] for p in available} == {p["name"] for p in catalog["plugins"]}
        print("Codex CLI: all 3 plugins discovered")
    else:
        print("Codex CLI unavailable: discovery smoke check skipped")
    print(f"Validated 3 portable packages, {skill_count} skills, {role_count} roles and internal links")


if __name__ == "__main__":
    main()
