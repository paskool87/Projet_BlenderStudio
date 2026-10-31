# MovieStudio Blender – État du projet

**Dernière mise à jour : 29 octobre 2026**

## 1. Objectif

Développer une extension Blender appelée MovieStudio pour préparer des objets importés, organiser leur visibilité et créer des animations sur la timeline.

Environnement :
- Blender 5.1.1
- Python intégré à Blender
- Extension Python modulaire
- Dépôt Git local : `C:\Users\pasca\Desktop\ProjetBlenderStudio\MovieStudio`

## 2. Architecture actuelle

```text
MovieStudio/
├── README.md
├── ETAT_PROJET.md
├── scenes/
│   ├── MovieStudio_Prototype.blend
│   └── MovieStudio_Prototype.blend1
└── src/
    ├── moviestudio.py
    └── moviestudio/
        ├── __init__.py
        ├── utils.py
        ├── import_fbx.py
        ├── preparation.py
        ├── timeline.py
        ├── environment.py
        ├── interface.py
        ├── selection.py
        └── visibility.py
```

Le fichier `src/moviestudio.py` est l'ancien prototype. Il doit être conservé intact.

Les scènes `.blend` existantes ne doivent pas être modifiées sans nécessité explicite.

## 3. Fonctionnalités en place

### Import et sélection
- Import de fichiers FBX depuis l'extension.
- Identification des objets importés par MovieStudio.
- Attribution d'un identifiant commun aux objets issus d'un même import.
- Bouton « Sélectionner les objets communs » dans le panneau latéral.
- Les groupes provenant d'importations différentes restent indépendants.

### Visibilité sur la timeline
- Deux champs de réglage : **Apparition** et **Disparition**.
- Les réglages sont appliqués aux objets appartenant au même groupe d'importation.
- La visibilité évolue en fonction de la frame courante.
- Aucun bouton d'activation supplémentaire n'est nécessaire.
- L'activation de l'extension a été corrigée pour éviter l'accès à `bpy.context.scene` dans un contexte Blender restreint.

### Préparation et animation
L'architecture comprend également des modules consacrés à :
- la préparation et à la validation des transformations ;
- l'insertion de keyframes sur la timeline ;
- la création du sol et du quadrillage ;
- l'interface du panneau MovieStudio.

Ces fonctionnalités devront être retestées si une modification ultérieure affecte leur fonctionnement.

## 4. Dernier état validé par l'utilisateur

Le 29 octobre 2026, l'utilisateur a confirmé que :
- la sélection des objets communs fonctionne ;
- les réglages Apparition et Disparition fonctionnent ;
- l'extension fonctionne à nouveau après correction de son enregistrement.

Un commit a été créé après cette validation.

**Identifiant et message exacts du commit :** à récupérer avec `git log -1 --oneline`. Ne pas inventer ces informations.

## 5. Prochaine étape : déplacement d'un personnage

**Objectif principal :** créer une fonction permettant de faire marcher un personnage d'un point A à un point B sur la timeline.

Cette fonctionnalité se décompose en deux étapes.

### Étape 1 – Normalisation des armatures à l'import

Avant de pouvoir appliquer une animation de marche de manière fiable, il faut disposer d'une structure d'armature cohérente.

Objectifs :
- Analyser les armatures des personnages importés.
- Identifier les différences de structure, d'orientation et de proportions.
- Définir une convention commune pour les armatures.
- Normaliser les personnages lors de leur importation.
- Vérifier que les animations peuvent être appliquées correctement après normalisation.

Cette étape doit permettre de travailler avec différents personnages sans devoir adapter manuellement chaque animation.

La méthode de normalisation devra être définie après examen de plusieurs personnages et de leurs armatures.

### Étape 2 – Fonction de déplacement avec marche

Créer un outil permettant de définir :
- Un point de départ A.
- Un point d'arrivée B.
- Une durée de déplacement sur la timeline.
- Une animation de marche adaptée au déplacement.

Comportement attendu :
- Le personnage se déplace de A vers B.
- L'animation de marche accompagne le déplacement.
- Le personnage est automatiquement orienté dans la direction du déplacement.
- La vitesse de déplacement est cohérente avec la durée définie.
- Le déplacement et l'animation sont intégrés à la timeline Blender.

À terme, cette fonction pourra évoluer vers des déplacements sur plusieurs points et des trajectoires plus complexes.

## 6. Améliorations secondaires en attente

Ces fonctionnalités restent prévues, mais ne constituent pas la prochaine priorité :

- Ajouter un bouton de sélection du groupe toujours accessible dans le viewport.
- Permettre de faire réapparaître un objet déjà importé sans devoir en importer un nouveau.

## 7. Méthode de travail

- Procéder par petites étapes.
- Modifier et tester directement dans Blender.
- Fournir le contenu complet de chaque fichier Python modifié.
- Conserver les identifiants du code en anglais et l'interface en français.
- Ne pas modifier les scènes existantes ni l'ancien prototype sans nécessité.
- Vérifier chaque fonctionnalité dans Blender avant de la considérer comme validée.
- Créer un commit après chaque étape fonctionnelle validée.

## 8. Point de reprise

Le dernier état fonctionnel de MovieStudio a été committé.

**Prochaine tâche : étudier et mettre en place la normalisation des armatures lors de l'import des personnages.**

Cette étape préparera directement la création de la fonction de marche entre deux points.
## Nouvelle orientation : gestion des personnages et des animations

### Rig de référence
- Abandon de MetaSynth comme rig cible.
- Utilisation du **Human Meta-Rig de Rigify** comme référence officielle de MovieStudio.
- Le rig généré par Rigify sera utilisé pour l'animation des personnages.
- Exploitation des os existants du corps, de la poitrine et du visage.

### Objectif
Permettre d'importer des personnages provenant de différentes sources, de les adapter au rig Rigify Human et de leur appliquer des animations prédéfinies du corps et du visage.

### Retargeting
- Correspondance des os : automatique avec possibilité de correction manuelle.
- Os indispensables manquants : correction manuelle obligatoire.
- Pose de référence des personnages : T ou A.
- Conservation des morphologies différentes : ne pas imposer une taille ou un gabarit unique.
- Suppression de l'armature source uniquement après validation de la conversion.

### Sources de personnages
- Mixamo : source fréquente de personnages riggés et d'animations corporelles.
- MakeHuman : source fréquente de personnages avec mesh des yeux.
- Autres sources : prise en charge souhaitée, sans limiter MovieStudio à ces deux solutions.

### Bibliothèque d'animations
- Première priorité : animations corporelles Mixamo converties vers Rigify.
- Constitution d'une bibliothèque d'animations réutilisables.
- Animations faciales prédéfinies dans une étape dédiée.
- Retargeting des animations FBX vers Rigify.

### Système facial à développer
- Exploitation des os faciaux du Human Meta-Rig.
- Gestion des yeux et de leur orientation.
- Gestion des paupières et des expressions.
- Étude d'une utilisation complémentaire des Shape Keys.
- Contrôles faciaux simplifiés dans MovieStudio.

### Organisation du code
Créer des dossiers dédiés dans `src/moviestudio/` :
- `characters/` : import, analyse des armatures, correspondance des os, transfert des poids et validation.
- `animations/` : import, retargeting, bibliothèque et lecture des animations.
- `facial/` : rig facial, contrôle des yeux et animations faciales.

### Extension Retarget
- Extension Blender installée dans `extensions/blender_org/retarget`.
- Utilisation envisagée pour le retargeting des armatures et animations.
- Étude de ses fonctions avant toute intégration.

### Prochaine étape
Examiner la structure du Human Meta-Rig Rigify dans Blender, notamment les os du corps, de la poitrine, du visage et des yeux, puis établir le référentiel de correspondance.

### État
Conception validée. Aucune modification de code réalisée pour cette nouvelle fonctionnalité.

## 9. Diagnostic des armatures : première étape validée

**Date : 31 octobre 2026**

### Module ajouté
- `characters/__init__.py`
- `characters/rig_analyzer.py`

### Interface
Ajout du bouton « Analyser le personnage » dans le panneau MovieStudio.

### Tests réalisés sur le personnage Mixamo

Armature `Armature` :
- Type détecté : MIXAMO.
- 65 os détectés.
- 65 os déformants.
- Pose en T détectée.
- Tous les os indispensables présents.

Meshes associés :
- `Beta_Surface` : 14 232 sommets, 50 groupes correspondants sur 50.
- `Beta_Joints` : 10 514 sommets, 39 groupes correspondants sur 39.
- Aucun groupe sans os correspondant.
- Tous les sommets disposent de pondérations correspondantes.

### Résultat
Diagnostic fonctionnel et validé dans Blender 5.1.1.

L'analyse est entièrement en lecture seule : aucune modification du personnage ou de son armature.

### Prochaine étape
Étudier et établir la correspondance entre les os Mixamo et le Meta-Rig Rigify.

Objectifs :
- Comparer les positions et orientations des os.
- Adapter le Meta-Rig à la pose en T du personnage.
- Préparer une correspondance corporelle fiable.
- Préserver les meshes, leurs pondérations et les éléments faciaux.