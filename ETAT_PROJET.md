# MovieStudio – État du projet

**Version de développement :** 0.7  
**Environnement :** Blender 5.1.1  
**Dernière mise à jour :** 31 octobre 2026

## 1. Objectif du projet

MovieStudio est un add-on Blender inspiré de MovieStorm. Il vise à simplifier la création de films 3D sans nécessiter une maîtrise complète de Blender.

Objectifs :
- Créer et organiser des décors.
- Importer et préparer des personnages.
- Gérer leur apparition et leur disparition dans la timeline.
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
- L'adaptation conserve autant que possible la structure Rigify nécessaire.
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

## 5. Adaptation géométrique du Meta-Rig

Le module `metarig_adapter.py` réalise désormais l'adaptation géométrique de la copie de travail du Meta-Rig aux proportions du personnage Mixamo.

### Correspondances adaptées

Le test a été réalisé sur le personnage Mixamo `Armature` :

| Élément | Résultat |
|---|---:|
| Os Mixamo détectés | 65 |
| Correspondances principales | 22 |
| Correspondances des doigts | 30 |
| Total des os adaptés | 52 |
| Os palm supprimés | 8 |
| Os ignorés | 0 |

Les correspondances principales couvrent :
- Bassin et colonne vertébrale.
- Cou et tête.
- Épaules, bras et mains.
- Cuisses, jambes et pieds.

Les 30 os des doigts sont également adaptés aux positions du squelette Mixamo.

### Suppression des os palm

Les huit os `palm` du Meta-Rig Rigify ne possèdent pas de correspondance dans le squelette Mixamo.

Le module les supprime automatiquement et transfère leurs enfants vers les os des mains correspondants, sans conserver de liaison incorrecte.

### Résultat du test

**Adaptation géométrique validée dans Blender.**

- 52 os adaptés.
- 8 os palm supprimés automatiquement.
- Aucun os ignoré.
- Copie de travail utilisée pour les modifications.
- Référence originale préservée.
- Personnage Mixamo original non modifié.

## 6. Prochaine étape : adaptation du visage

La prochaine étape consiste à diagnostiquer les os faciaux du personnage Mixamo et ceux du Meta-Rig avant toute modification.

Objectifs :
1. Identifier les os des yeux et de la mâchoire présents dans le squelette Mixamo.
2. Comparer leurs positions avec celles du Meta-Rig.
3. Déterminer les os faciaux Rigify qui doivent être adaptés.
4. Préserver la structure faciale et les contrôleurs Rigify.
5. Vérifier le résultat avant la génération du rig.

Aucune adaptation faciale ne doit être effectuée avant d'avoir obtenu les données réelles des deux squelettes.

Le rig final et le retargeting seront traités dans des étapes ultérieures.

## 7. Règles de développement

- Travailler étape par étape.
- Fournir le contenu complet de chaque fichier modifié.
- Tester chaque étape dans Blender avant de poursuivre.
- Ne jamais modifier le personnage original pendant la préparation.
- Conserver la référence Meta-Rig intacte.
- Effectuer un commit Git après chaque étape stable.
- Mettre à jour ce fichier après chaque commit.