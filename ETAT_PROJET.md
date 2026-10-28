# MovieStudio - État du projet

Dernière mise à jour : 28 octobre 2026

## Objectif

Développer progressivement une extension Blender inspirée de MovieStorm pour créer des décors, importer des objets et personnages, placer des caméras et animer les transformations des objets sur une timeline.

## Environnement

- Blender 5.1.1
- Python intégré à Blender : 3.13.9
- Projet versionné avec Git
- Extension installée localement dans le profil Blender de l'utilisateur

## Architecture

- `src/moviestudio.py` : prototype historique version 0.6.0, conservé comme référence.
- `src/moviestudio/__init__.py` : métadonnées et enregistrement de l'extension.
- `src/moviestudio/utils.py` : propriétés personnalisées et fonctions utilitaires.
- `src/moviestudio/import_fbx.py` : importation FBX.
- `src/moviestudio/preparation.py` : validation des transformations.
- `src/moviestudio/timeline.py` : insertion des images clés.
- `src/moviestudio/environment.py` : création du sol quadrillé.
- `src/moviestudio/interface.py` : panneau MovieStudio dans la vue 3D.
- `scenes/MovieStudio_Prototype.blend` : scène du prototype.
- `scenes/MovieStudio_Prototype.blend1` : sauvegarde Blender conservée.

## Réalisations

- Répartition du code du prototype en plusieurs modules Python.
- Conservation du fichier historique `src/moviestudio.py`.
- Création du panneau MovieStudio et de ses six classes enregistrables.
- Importation FBX avec identification des objets importés.
- Validation des rotations et des échelles sans appliquer la position.
- Insertion d'images clés de position, rotation et échelle.
- Création d'un sol quadrillé avec affichage des faces et des arêtes.
- Installation locale du package dans le dossier des extensions Blender.

## Vérifications effectuées

- Syntaxe Python vérifiée pour les sept fichiers du package.
- Import du package réussi dans Blender 5.1.1.
- Enregistrement et désenregistrement des six classes réussis.
- Panneau MovieStudio affiché dans la vue 3D.
- Installation locale et activation de l'extension vérifiées.

## Points restant à tester

- Importation d'un fichier FBX réel.
- Validation des transformations sur des objets de test.
- Insertion et lecture des images clés sur la timeline.
- Création du sol quadrillé après la correction de son affichage.
- Vérification du rechargement de l'extension après une modification du code source.

## Règles de travail

- Conserver `src/moviestudio.py` comme référence historique.
- Ne pas déplacer ni supprimer les fichiers `.blend` sans décision explicite.
- Développer et vérifier les fonctionnalités progressivement.
- Mettre à jour ce document à chaque étape importante.

## Prochaine étape

Tester individuellement les fonctionnalités depuis l'interface Blender, puis poursuivre le développement des déplacements d'objets sur la timeline.