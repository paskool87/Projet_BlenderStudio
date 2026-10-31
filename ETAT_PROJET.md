# MovieStudio – État du projet

**Version de développement :** 0.7  
**Environnement :** Blender 5.1.1  
**Dernière mise à jour :** 31 octobre 2026

## 1. Objectif du projet

MovieStudio est un add-on Blender inspiré de MovieStorm. Il vise à simplifier la création de films 3D sans nécessiter une maîtrise complète de Blender.

Objectifs :
- Créer et organiser des décors.
- Importer et préparer des personnages.
- Gérer leur apparition et disparition dans la timeline.
- Créer des déplacements et animations.
- Gérer les caméras et les expressions.

La conversion FBX vers CAF/Cal3D/MovieStorm est abandonnée. Le projet utilise directement les outils d'animation de Blender.

## 2. Fonctionnalités déjà validées

- Import de fichiers FBX.
- Identification et regroupement des objets importés.
- Sélection des objets d'un même groupe.
- Gestion de l'apparition et de la disparition dans la timeline.
- Synchronisation de la visibilité avec les images de la timeline.
- Préparation et validation des transformations.
- Création du sol et du quadrillage.

## 3. Architecture actuelle

Le projet est organisé en modules Python :

```text
src/moviestudio/
├── __init__.py
├── utils.py
├── import_fbx.py
├── preparation.py
├── timeline.py
├── environment.py
├── interface.py
├── selection.py
├── visibility.py
├── characters/
│   ├── __init__.py
│   ├── rig_analyzer.py
│   ├── rig_comparator.py
│   ├── metarig_template.py
│   └── metarig_adapter.py
└── resources/
    └── reference_metarig.blend
```

Les scènes Blender sont conservées dans le dossier `scenes/`.

## 4. Système de préparation des personnages

### Référence officielle

Le projet utilise le Human Meta-Rig de Rigify comme référence universelle.

Principes :
- La référence originale reste intacte.
- Chaque personnage dispose d'une copie de travail indépendante.
- L'adaptation conserve la structure Rigify.
- Le personnage original et son armature ne sont jamais modifiés.
- Le rig final sera généré ultérieurement avec Rigify.

### Diagnostic des personnages

Le module `rig_analyzer.py` permet :
- De détecter les armatures Mixamo.
- D'identifier les meshes associés.
- D'analyser les os et leurs hiérarchies.
- D'extraire les positions en coordonnées monde.
- De vérifier les caractéristiques d'une T-pose.
- D'analyser les poids des meshes.

### Comparateur

Le module `rig_comparator.py` contient les correspondances entre les os Mixamo et le Meta-Rig.

Le comparateur a été testé sur un personnage Mixamo :
- 20 correspondances comparées.
- Identification des écarts de position et d'orientation.
- Confirmation des différences entre la T-pose Mixamo et l'A-pose du Meta-Rig.

### Template Meta-Rig

Le module `metarig_template.py` permet :
- De charger la référence depuis `reference_metarig.blend`.
- De conserver une référence masquée dans la scène.
- De créer une copie indépendante du Meta-Rig.
- De garantir l'indépendance des données d'armature.

Test validé : copie de 159 os, indépendante de la référence.

## 5. Dernière étape validée : préparation de l'adaptation

Le module `metarig_adapter.py` permet désormais de détecter automatiquement le personnage Mixamo dans la scène et de préparer les positions correspondantes.

Test réalisé avec un personnage Mixamo importé :

| Élément | Résultat |
|---|---:|
| Armature détectée | Armature |
| Nombre d'os Mixamo | 65 |
| Correspondances | 22 |
| Positions préparées | 22 |
| Modifications géométriques | Aucune |

Les correspondances couvrent :
- Bassin et colonne vertébrale.
- Cou et tête.
- Épaules, bras et mains.
- Cuisses, jambes et pieds.

**Résultat :** préparation réussie. Aucune modification géométrique n'a encore été effectuée.

## 6. Prochaine étape

Développer l'adaptation géométrique réelle de la copie du Meta-Rig.

Objectifs :
1. Adapter les positions des os aux proportions du personnage Mixamo.
2. Adapter les bras à sa T-pose.
3. Préserver la hiérarchie et la structure Rigify.
4. Préserver les contrôleurs faciaux.
5. Ne jamais modifier le personnage original.
6. Vérifier visuellement et géométriquement le résultat avant de poursuivre.

Le rig final et le retargeting seront traités dans des étapes ultérieures.

## 7. Règles de développement

- Travailler étape par étape.
- Fournir le contenu complet de chaque fichier modifié.
- Tester chaque étape dans Blender avant de poursuivre.
- Ne jamais modifier le personnage original pendant la préparation.
- Conserver la référence Meta-Rig intacte.
- Effectuer un commit Git après chaque étape stable.
- Mettre à jour ce fichier après chaque commit.
