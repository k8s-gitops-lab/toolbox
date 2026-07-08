#!/usr/bin/env python3
"""Verifie que <app>/.gitlab-ci.yml declare les memes variables que celles
derivees de l'inventaire argocd/apps/<app>.yaml (platform-gitops).

L'inventaire est cense etre la source de verite unique de l'app (App
standard, cf. cockpit/CONTEXT.md) mais SERVICES/SERVICE_NAME/
MANIFESTS_PROJECT_PATH/MANIFESTS_PATH/HAS_PREPROD sont aujourd'hui recopies
a la main dans le .gitlab-ci.yml de l'app, sans controle. Ce script rend
cette source de verite opposable en detectant toute derive.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from platform_inventory import load_inventory


def expected_variables(app: dict) -> dict[str, str]:
    services = " ".join(f"{s['name']}={s['image']}" for s in app["services"])
    return {
        "APP_NAME": app["name"],
        "SERVICES": services,
        "SERVICE_NAME": app["showcaseService"],
        "MANIFESTS_PROJECT_PATH": app["manifests"]["projectPath"],
        "MANIFESTS_PATH": app["manifests"]["path"],
        "HAS_PREPROD": "true" if app.get("hasPreprod") else "false",
    }


def actual_variables(gitlab_ci_file: Path) -> dict[str, str]:
    data = yaml.safe_load(gitlab_ci_file.read_text()) or {}
    return {k: str(v) for k, v in (data.get("variables") or {}).items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", help="Nom de l'app (doit exister dans l'inventaire)")
    parser.add_argument("--gitlab-ci-file", required=True,
                         help="Chemin vers <app>/.gitlab-ci.yml")
    parser.add_argument("--apps-file",
                         help="Chemin vers argocd/apps.yaml (defaut: cf. platform_inventory.default_apps_file)")
    args = parser.parse_args()

    inventory = load_inventory(Path(args.apps_file) if args.apps_file else None)
    apps = {a["name"]: a for a in inventory["apps"]}
    if args.app not in apps:
        sys.exit(f"App inconnue dans l'inventaire: {args.app} (connues: {', '.join(sorted(apps))})")

    expected = expected_variables(apps[args.app])
    actual = actual_variables(Path(args.gitlab_ci_file))

    drift = {
        key: (value, actual.get(key))
        for key, value in expected.items()
        if actual.get(key) != value
    }
    if drift:
        print(f"==> derive detectee entre l'inventaire et {args.gitlab_ci_file} :")
        for key, (exp, act) in drift.items():
            print(f"    {key}: inventaire={exp!r} .gitlab-ci.yml={act!r}")
        return 1

    print(f"OK: {args.gitlab_ci_file} coherent avec l'inventaire ({args.app}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
