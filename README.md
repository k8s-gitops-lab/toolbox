# toolbox

Scripts partagés pour piloter les projets `poc-devops`.

Ce repo porte le détail technique du **Parcours 2** décrit dans
[`control-plane/README.md`](../control-plane/README.md#parcours-2--une-équipe-applicative-crée-un-projet) :
comment une équipe applicative onboarde un projet sur une plateforme déjà en
place. Pour le bootstrap de la plateforme elle-même (Parcours 1), voir
`control-plane`.

Les scripts de bootstrap restent utilisables depuis `platform-cicd`. Cette
toolbox contient une copie réutilisable des utilitaires Python, avec une racine
GitOps configurable. Par defaut, cette racine est `../platform-gitops`.

## Installation

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Ajouter un projet sans checkout GitOps

Pour ajouter un projet standard comme `helloworld`, le developpeur n'a pas
besoin de cloner `platform-gitops`. Depuis le dossier qui contient les
dépôts `helloworld` et `helloworld-iac`:

```sh
PLATFORM_REPO_URL=https://github.com/poc-devops-elkouhen/platform-gitops.git \
GITHUB_TOKEN=<token> \
python3 /chemin/toolbox/scripts/init-project.py helloworld
```

Le script clone temporairement le dépôt GitOps, ajoute ou met à jour
`argocd/apps/helloworld/`, pousse une branche `toolbox/add-helloworld`, puis
ouvre une pull request.

Au merge de cette pull request, le pipeline `.gitlab-ci.yml` du projet
GitLab `platform-gitops` (développé sur GitLab, mirroré vers GitHub)
déclenche automatiquement, sans action supplémentaire :

1. la régénération des manifests ArgoCD (`AppProject`/`ApplicationSet`) via
   `platform-cicd/scripts/render-argocd-apps.py` ;
2. la régénération de `gitlab-projects-iac/terraform/apps.auto.tfvars.json`
   via `render-gitlab-projects.py` (voir "Scripts" ci-dessous), qui fait
   ensuite créer ou mettre à jour le projet GitLab applicatif via Terraform.

Les credentials ArgoCD pour accéder au dépôt manifests privé sont
provisionnés séparément par `argocd-repo-creds.py` (voir "Utilisation avec
checkout GitOps").

Si les dépôts applicatifs sont dans un autre dossier:

```sh
PLATFORM_REPO_URL=https://github.com/poc-devops-elkouhen/platform-gitops.git \
GITHUB_TOKEN=<token> \
PROJECTS_DIR=/chemin/projets \
python3 /chemin/toolbox/scripts/init-project.py helloworld
```

Les URLs Git restent possibles lorsque le développeur n'a pas non plus les
dépôts applicatifs en local:

```sh
PLATFORM_REPO_URL=https://github.com/poc-devops-elkouhen/platform-gitops.git \
GITHUB_TOKEN=<token> \
python3 /chemin/toolbox/scripts/init-project.py \
  https://git.example.com/team/helloworld.git \
  https://git.example.com/team/helloworld-iac.git
```

## Supprimer un projet sans checkout GitOps

Pour retirer `helloworld` de la plateforme sans cloner `platform-gitops`:

```sh
PLATFORM_REPO_URL=https://github.com/poc-devops-elkouhen/platform-gitops.git \
GITHUB_TOKEN=<token> \
python3 /chemin/toolbox/scripts/delete-project.py helloworld
```

Le script supprime l'entrée `argocd/apps/helloworld/` du dépôt GitOps, pousse
une branche `toolbox/delete-helloworld`, puis ouvre une pull request. Il ne
supprime pas les dépôts GitLab applicatifs.

## Utilisation avec checkout GitOps

Depuis le dépôt GitOps, pour les opérations d'administration:

```sh
PLATFORM_REPO_ROOT="$PWD" python3 ../toolbox/scripts/init-project.py helloworld
PLATFORM_REPO_ROOT="$PWD" python3 ../toolbox/scripts/init-project.py ../helloworld ../helloworld-iac
PLATFORM_REPO_ROOT="$PWD" python3 ../toolbox/scripts/delete-project.py helloworld
PLATFORM_REPO_ROOT="$PWD" python3 ../toolbox/scripts/argocd-repo-creds.py
python3 ../toolbox/scripts/render-gitlab-projects.py
```

Le token runner GitLab (`gitlab-runner-token.py`) est un script de bootstrap
plateforme, pas d'onboarding applicatif : il vit dans `platform-cicd/scripts/`
(voir `platform-cicd/AGENTS.md`).

Depuis n'importe quel autre répertoire, renseigner `PLATFORM_REPO_ROOT` avec le chemin absolu du dépôt `platform-gitops`.

## Scripts

- `init-project.py` et `init_projects/`: ajoute ou met à jour une app dans `argocd/apps/<app>/`.
- `delete-project.py` et `delete_projects.py`: supprime une app de `argocd/apps/<app>/` et ouvre une pull/merge request en mode `PLATFORM_REPO_URL`.
- `render-gitlab-projects.py`: génère `apps.auto.tfvars.json` (liste des apps + description) pour `gitlab-projects-iac`, à partir de l'inventaire `platform-gitops`.
- `argocd-repo-creds.py`: crée les credentials ArgoCD pour les dépôts manifests privés.
- `get-gitlab-token.py`: récupère un token GitLab pour les opérations locales.
- `platform_inventory.py`: modèle de données partagé (chargement et normalisation de l'inventaire) ; une copie synchronisée existe dans `platform-cicd/scripts/`.
- Les projets GitLab et dépôts applicatifs sont déclarés dans `gitlab-projects-iac`
  puis appliqués par le `Terraform/gitlab-iac`.

## Variables utiles

- `PLATFORM_REPO_ROOT`: racine du dépôt GitOps. Par defaut: `../platform-gitops`.
- `PLATFORM_REPO_URL`: URL GitHub du dépôt GitOps source. Si renseignée, les scripts projet ouvrent une pull request au lieu d'écrire dans un checkout local.
- `GITHUB_TOKEN`: token utilisé pour cloner/pousser le dépôt GitOps GitHub et créer la pull request.
- `GITLAB_TOKEN`: token utilisé pour les opérations contre le GitLab de la plateforme (credentials ArgoCD).
- `PROJECTS_DIR`: dossier contenant les dépôts applicatifs lorsque `init-project.py` est appelé avec un nom de projet. Par défaut: répertoire courant en mode `PLATFORM_REPO_URL`, sinon dossier parent du dépôt GitOps.
- `APPS_FILE`: chemin explicite vers l'inventaire apps.
- `APPS_DIR`: dossier contenant les fichiers app YAML.
- `GITLAB_NAMESPACE`, `GITLAB_URL`, `ARGOCD_NAMESPACE`: paramètres Kubernetes/GitLab utilisés par les scripts de bootstrap.
