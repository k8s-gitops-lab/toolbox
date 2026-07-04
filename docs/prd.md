# PRD

## Intention du projet

`toolbox` regroupe les scripts réutilisables pour piloter les
projets du POC sans dépendre directement d'un checkout actif de
`platform-cicd`.

La vision globale, le modèle d'onboarding et les limites du POC sont dans
`../../control-plane/docs/prd.md`.

## Produit attendu

La toolbox doit permettre :

- de supprimer une application de l'inventaire plateforme (l'ajout se fait
  par MR directe sur `platform-gitops`, sans script) ;
- de générer `apps.auto.tfvars.json` pour `gitlab-projects-iac` depuis
  l'inventaire ;
- de créer les credentials ArgoCD pour les dépôts manifests privés ;
- de récupérer un token GitLab utile aux opérations locales.

## Utilisateurs cibles

- Développeur applicatif qui veut onboarder une app sans manipuler toute la
  plateforme.
- Mainteneur plateforme qui veut exécuter les scripts partagés depuis un dépôt
  dédié.
- Automatisation future qui ouvrira des pull/merge requests vers la plateforme.

## Critères d'acceptation

- Les scripts acceptent `PLATFORM_REPO_ROOT` pour travailler avec un checkout
  local.
- Les scripts acceptent `PLATFORM_REPO_URL` et `GITHUB_TOKEN` pour travailler
  via clone temporaire et pull request GitHub. Cette URL doit pointer vers le
  dépôt GitOps source sur GitHub.
- La suppression retire l'entrée d'application sans supprimer les dépôts
  applicatifs.
- Les commandes principales sont disponibles depuis le `Makefile`.

## Non-objectifs

- Remplacer la documentation fonctionnelle de la plateforme.
- Devenir une dépendance implicite non déclarée du bootstrap plateforme.
- Supprimer physiquement des dépôts applicatifs GitLab lors d'un delete.
