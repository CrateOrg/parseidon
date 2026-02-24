import os
import sys
import tomllib

ci_tag = os.environ["CI_COMMIT_TAG"]
tag = ci_tag.lstrip("v")

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

version = data.get("project", {}).get("version")

if tag != version:
    print(f"❌ Tag ({ci_tag}) does not match pyproject.toml version ({version})")
    sys.exit(1)

print(f"✅ Tag {ci_tag} matches version: {version}")
