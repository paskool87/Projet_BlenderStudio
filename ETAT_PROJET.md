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

## 5. Limites et améliorations à venir

### Priorité 1 – Sélection accessible depuis le viewport
Ajouter un bouton de sélection du groupe toujours accessible dans la vue 3D, sans devoir ouvrir le panneau latéral à chaque utilisation.

Le mécanisme exact reste à définir lors de l'implémentation.

### Priorité 2 – Réapparition des objets existants
Actuellement, pour faire réapparaître un objet semblable, l'utilisateur doit importer un nouvel objet.

Il faut étudier une solution permettant de réutiliser les objets déjà importés et de modifier leur période de visibilité, sans importation supplémentaire.

### Étapes suivantes
Après ces deux améliorations :
- tester les changements directement dans Blender ;
- vérifier que les groupes restent indépendants ;
- vérifier le comportement aux frames d'apparition et de disparition ;
- créer un nouveau commit après validation réelle.

## 6. Méthode de travail

- Procéder par petites étapes.
- Modifier et tester directement dans Blender, sans créer de fichiers de test séparés.
- Fournir le contenu complet de chaque fichier Python modifié, jamais uniquement des extraits.
- Conserver les identifiants du code en anglais et l'interface utilisateur en français.
- Ne pas toucher aux scènes existantes ni à l'ancien prototype sans raison.
- Ne pas annoncer un test réussi sans résultat vérifié.
- Créer un commit à la fin d'une étape fonctionnelle validée.

## 7. Point de reprise

Reprendre à partir du dernier commit validé.

**Prochaine tâche :** rendre le bouton de sélection d'un groupe d'importation accessible en permanence depuis la vue 3D de Blender.

Ne pas reprendre les fonctionnalités déjà validées. Traiter ensuite le problème de réapparition des objets existants.
