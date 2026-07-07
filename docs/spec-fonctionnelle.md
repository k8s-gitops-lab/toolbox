# Spec fonctionnelle

## Ajouter une application

Pas de script : l'utilisateur ouvre directement une pull/merge request sur
`platform-gitops` ajoutant `argocd/apps/<app>.yaml` (name, description,
services, hasPreprod). Voir "Onboarding automatique via MR" plus bas pour ce
qui se déclenche au merge.

## Supprimer une application

`delete-project.py` retire le dossier d'application de l'inventaire GitOps et
ouvre une pull/merge request en mode distant. La suppression ne détruit ni les
dépôts GitLab ni les ressources déjà déployées.

## Seeder et administrer

La toolbox expose aussi :

- `get-gitlab-token.py` pour récupérer un token d'administration local.

Les credentials manifests d'ArgoCD ne passent plus par la toolbox : ils sont
fabriqués en continu par External Secrets Operator.

La création ou mise à jour des projets GitLab est portée par
`gitlab-projects-iac`, appliqué par le `Terraform/gitlab-iac`.

## Onboarding automatique via MR

Une MR sur le projet GitLab `platform-gitops` ajoutant `argocd/apps/<app>.yaml`
(name, description, services) déclenche directement, au merge sur `main`, le
pipeline `.gitlab-ci.yml` de ce projet. Ce pipeline régénère automatiquement
les manifests ArgoCD (commit sur le même projet GitLab, mirroré vers GitHub) et
le fichier `apps.auto.tfvars.json` de `gitlab-projects-iac` (commit direct sur
GitHub, dépôt canonique surveillé par ArgoCD/Flux). L'utilisateur n'a plus
qu'à écrire ce seul fichier ; tout le reste (conf ArgoCD, projets GitLab —
créés vides, sans import GitHub, sauf apps historiques marquées
`importFromGithub: true`) est dérivé et committé par le bot.

## Modes d'utilisation

Deux modes sont supportés :

- checkout local avec `PLATFORM_REPO_ROOT` ;
- dépôt distant avec `PLATFORM_REPO_URL` et `GITHUB_TOKEN` pour GitHub.

Le mode distant est celui attendu pour un utilisateur qui ne veut pas cloner
manuellement `platform-gitops`.
