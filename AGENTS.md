# AGENTS.md — toolbox

## Rôle du dépôt

`toolbox` regroupe les scripts d'opération plateforme utilisables indépendamment
de `platform-cicd`. Il permet de retirer des applications et de gérer les
credentials ArgoCD sans checkout actif de `platform-cicd`. L'ajout d'une
application se fait par pull/merge request directe sur `platform-gitops`
(pas de script dédié, voir "Pipeline d'onboarding automatique" ci-dessous).

## Fichiers clés

| Fichier | Rôle |
|---------|------|
| `scripts/platform_inventory.py` | Modèle de données partagé (chargement et normalisation de l'inventaire) |
| `scripts/render-gitlab-projects.py` | Génère `apps.auto.tfvars.json` (liste des apps + description) pour `gitlab-projects-iac`, à partir de l'inventaire `platform-gitops` |
| `scripts/get-gitlab-token.py` | Récupère un token GitLab pour les opérations locales |
| `scripts/delete-project.py` / `delete_projects.py` | Suppression d'apps de l'inventaire |
| `scripts/check-app-gitlab-ci.py` | Vérifie que `<app>/.gitlab-ci.yml` (SERVICES, SERVICE_NAME, MANIFESTS_PROJECT_PATH, MANIFESTS_PATH, HAS_PREPROD) n'a pas dérivé de l'inventaire |

## Modes de fonctionnement

**Mode local** — dépôt `platform-gitops` cloné localement :
```bash
PLATFORM_REPO_ROOT=../platform-gitops make check-app-gitlab-ci APP=helloworld GITLAB_CI_FILE=../helloworld/.gitlab-ci.yml
```

**Mode MR** — clone temporaire depuis GitHub :
```bash
PLATFORM_REPO_URL=https://github.com/k8s-gitops-lab/platform-gitops \
GITHUB_TOKEN=<token> python3 scripts/delete-project.py helloworld
```

Les projets GitLab ne sont plus seedés depuis `toolbox`. Ils sont déclarés dans
`gitlab-projects-iac` (fichier généré `apps.auto.tfvars.json`, produit par
`render-gitlab-projects.py`) et appliqués par le `Terraform/gitlab-iac`.

## Pipeline d'onboarding automatique

Depuis l'automatisation ajoutée dans `platform-gitops` (pipeline
`.gitlab-ci.yml` du projet GitLab `platform-gitops`, développé directement sur
GitLab et mirroré vers GitHub), une simple MR ajoutant
`argocd/apps/<app>.yaml` (avec au minimum `name`, `description` et `services`)
suffit à déclencher :
1. la régénération des manifests ArgoCD (`platform-cicd/scripts/render-argocd-apps.py`) ;
2. la régénération de `gitlab-projects-iac/terraform/apps.auto.tfvars.json`
   (`toolbox/scripts/render-gitlab-projects.py`), qui fait ensuite créer/mettre
   à jour les projets GitLab via Terraform.

Le champ `description` est optionnel, transparent pour `_normalize_app`
(copié tel quel), et propagé à la fois dans l'`AppProject` ArgoCD
(`spec.description`) et dans la description du projet GitLab. Le champ
`importFromGithub` (optionnel, défaut `false`) ne doit être mis à `true` que
pour une app dont le code préexiste déjà sur GitHub avant onboarding — les
nouvelles apps sont créées vides sur GitLab.

## Vérifier la cohérence inventaire / .gitlab-ci.yml

`<app>/.gitlab-ci.yml` recopie à la main des faits déjà présents dans
`argocd/apps/<app>.yaml` (services, `hasPreprod`, chemin des manifests...).
Rien ne les garde synchronisés automatiquement ; `check-app-gitlab-ci.py`
détecte la dérive au lieu de la laisser silencieuse :

```bash
PLATFORM_REPO_ROOT=../platform-gitops \
  make check-app-gitlab-ci APP=helloworld GITLAB_CI_FILE=../helloworld/.gitlab-ci.yml
```

À lancer après toute modification de l'inventaire d'une app ou de son
`.gitlab-ci.yml`. Pas encore branché dans une pipeline CI (le job
`onboard-apps` de `platform-gitops` ne clone pas les dépôts applicatifs) —
vérification manuelle pour l'instant.

## Variables d'environnement importantes

| Variable | Rôle |
|----------|------|
| `PLATFORM_REPO_ROOT` | Chemin local vers `platform-gitops` |
| `PLATFORM_REPO_URL` | URL GitHub pour clone temporaire (mode MR) |
| `GITLAB_URL` | URL externe GitLab (défaut : `https://gitlab.192.168.33.100.nip.io`) |
| `GITLAB_NAMESPACE` | Namespace K8s GitLab (défaut : `gitlab`) |

## Ce qu'il ne faut pas faire

- Ne pas modifier `platform_inventory.py` sans répercuter le changement dans
  `platform-cicd/scripts/platform_inventory.py` — les deux fichiers doivent
  rester synchronisés.
- Ne pas supprimer physiquement les dépôts GitLab applicatifs depuis les scripts
  de suppression — ils retirent uniquement l'entrée de l'inventaire.
- Ne pas committer de tokens ou mots de passe dans ce dépôt.
