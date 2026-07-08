# Spec technique

## Structure

- `Makefile` enveloppe les commandes principales.
- `scripts/delete-project.py` supprime une app de l'inventaire.
- `scripts/platform_git.py` gère les opérations Git/MR en mode distant.
- `scripts/platform_inventory.py` lit l'inventaire GitOps.

## Configuration

Les variables principales sont :

- `PLATFORM_REPO_ROOT` ;
- `PLATFORM_REPO_URL` ;
- `GITHUB_TOKEN` ;
- `GITLAB_TOKEN` ;
- `PROJECTS_DIR` ;
- `APPS_FILE` ;
- `APPS_DIR` ;
- `GITLAB_NAMESPACE` ;
- `GITLAB_URL` ;
- `ARGOCD_NAMESPACE`.

## Onboarding

L'ajout d'une app se fait par pull/merge request directe sur `platform-gitops`
ajoutant `argocd/apps/<app>.yaml` — pas de script dédié dans `toolbox`. Le
module `init_projects` restant ne porte plus que la résolution du dossier
`apps/` (`_resolve_apps_dir`), partagée avec le flux de suppression.

La synchronisation des projets GitLab n'est plus portée par `toolbox` : les
projets sont déclarés dans `gitlab-projects-iac` puis appliqués par le
`Terraform/gitlab-iac`. `scripts/render-gitlab-projects.py` génère le fichier
`apps.auto.tfvars.json` consommé par ce Terraform à partir du même inventaire
(`argocd/apps.yaml` + `argocd/apps/*.yaml`), avec un objet `{name, description}`
par app.

## Maintenance

Le bootstrap technique reste dans `platform-bootstrap`. La toolbox opère sur
`platform-gitops` par défaut via `PLATFORM_REPO_ROOT`, afin que les opérations
d'onboarding et de génération ciblent le dépôt suivi par ArgoCD.
