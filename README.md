# toolbox

Scripts partagés pour piloter les projets `poc-devops`.

Ce repo porte le détail technique du **Parcours 2** décrit dans
[`cockpit/README.md`](../cockpit/README.md#parcours-2--une-équipe-applicative-crée-un-projet) :
comment une équipe applicative onboarde un projet sur une plateforme déjà en
place. Pour le bootstrap de la plateforme elle-même (Parcours 1), voir
`cockpit`.

Les scripts de bootstrap restent utilisables depuis `platform-bootstrap`. Cette
toolbox contient une copie réutilisable des utilitaires Python, avec une racine
GitOps configurable. Par defaut, cette racine est `../platform-gitops`.

## Installation

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Ajouter un projet

Il n'y a pas de script d'onboarding : l'équipe applicative ouvre directement
une pull/merge request sur `platform-gitops` ajoutant
`argocd/apps/<app>.yaml`. Le merge déclenche automatiquement toute la chaîne
(rendu ArgoCD, inventaire Terraform, création des projets GitLab) — détail
dans `platform-gitops/docs/spec-fonctionnelle.md`, section "Flux d'onboarding
d'une application".

Les credentials ArgoCD pour accéder au dépôt manifests privé sont
fabriqués en continu par External Secrets Operator (ExternalSecrets générés
par `platform-bootstrap/scripts/render-argocd-apps.py`) : aucune action toolbox.

## Supprimer un projet sans checkout GitOps

Pour retirer `helloworld` de la plateforme sans cloner `platform-gitops`:

```sh
PLATFORM_REPO_URL=https://github.com/k8s-gitops-lab/platform-gitops.git \
GITHUB_TOKEN=<token> \
python3 /chemin/toolbox/scripts/delete-project.py helloworld
```

Le script supprime l'entrée `argocd/apps/helloworld.yaml` du dépôt GitOps, pousse
une branche `toolbox/delete-helloworld`, puis ouvre une pull request. Il ne
supprime pas les dépôts GitLab applicatifs.

## Utilisation avec checkout GitOps

Depuis le dépôt GitOps, pour les opérations d'administration:

```sh
PLATFORM_REPO_ROOT="$PWD" python3 ../toolbox/scripts/delete-project.py helloworld
python3 ../toolbox/scripts/render-gitlab-projects.py
```

Le token runner GitLab (`gitlab-runner-token.py`) est un script de bootstrap
plateforme, pas d'onboarding applicatif : il vit dans `platform-bootstrap/scripts/`
(voir `platform-bootstrap/AGENTS.md`).

Depuis n'importe quel autre répertoire, renseigner `PLATFORM_REPO_ROOT` avec le chemin absolu du dépôt `platform-gitops`.

## Scripts

- `delete-project.py` et `delete_projects.py`: supprime une app de `argocd/apps/<app>.yaml` et ouvre une pull/merge request en mode `PLATFORM_REPO_URL`.
- `render-gitlab-projects.py`: génère `apps.auto.tfvars.json` (liste des apps + description) pour `gitlab-projects-iac`, à partir de l'inventaire `platform-gitops`.
- `get-gitlab-token.py`: récupère un token GitLab pour les opérations locales.
- `platform_inventory.py`: modèle de données partagé (chargement et normalisation de l'inventaire) ; une copie synchronisée existe dans `platform-bootstrap/scripts/`.
- Les projets GitLab et dépôts applicatifs sont déclarés dans `gitlab-projects-iac`
  puis appliqués par le `Terraform/gitlab-iac`.

## Variables utiles

- `PLATFORM_REPO_ROOT`: racine du dépôt GitOps. Par defaut: `../platform-gitops`.
- `PLATFORM_REPO_URL`: URL GitHub du dépôt GitOps source. Si renseignée, les scripts projet ouvrent une pull request au lieu d'écrire dans un checkout local.
- `GITHUB_TOKEN`: token utilisé pour cloner/pousser le dépôt GitOps GitHub et créer la pull request.
- `GITLAB_TOKEN`: token utilisé pour les opérations contre le GitLab de la plateforme (credentials ArgoCD).
- `APPS_FILE`: chemin explicite vers l'inventaire apps.
- `APPS_DIR`: dossier contenant les fichiers app YAML.
- `GITLAB_NAMESPACE`, `GITLAB_URL`, `ARGOCD_NAMESPACE`: paramètres Kubernetes/GitLab utilisés par les scripts de bootstrap.
