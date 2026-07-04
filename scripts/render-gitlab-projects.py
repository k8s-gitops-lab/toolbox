#!/usr/bin/env python3
"""Generate gitlab-projects-iac/terraform/apps.auto.tfvars.json from the app inventory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from platform_inventory import default_apps_file, load_inventory


def apps_tfvars(apps_file: Path) -> dict:
    inventory = load_inventory(apps_file)
    apps = [
        {
            "name": app["name"],
            "group": app["group"],
            "description": app.get("description", ""),
            "importFromGithub": app.get("importFromGithub", False),
        }
        for app in inventory["apps"]
    ]
    return {"apps": apps}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apps-file", type=Path, default=default_apps_file())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tfvars = apps_tfvars(args.apps_file.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(tfvars, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(tfvars['apps'])} app(s) ecrite(s) dans {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
