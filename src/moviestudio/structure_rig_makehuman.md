# MovieStudio – Structure de référence du rig MakeHuman

**Version de référence :** MakeHuman `default`  
**Logiciel :** Blender 5.1  
**Rôle :** Squelette de référence pour la bibliothèque d'animations et d'expressions de MovieStudio.

## 1. Objectif

MovieStudio utilisera le rig natif MakeHuman `default` comme structure de référence pour tous les personnages.

L'objectif est de constituer une bibliothèque d'animations réutilisables :
- Animations corporelles : marche, course, gestes, postures.
- Expressions faciales : sourire, colère, tristesse, surprise.
- Animations du regard : mouvements des yeux et de la tête.
- Animation de la parole : mouvements de la mâchoire, de la bouche et de la langue.

Les animations devront pouvoir être combinées sans que l'une écrase les autres.

## 2. Organisation générale du squelette

### A. Racine et bassin
- `root` : racine générale du personnage.
- `pelvis.L` : bassin gauche.
- `pelvis.R` : bassin droit.

Particularité : les deux os du bassin sont directement rattachés à `root`. Il n'existe pas d'os unique nommé `hips`.

### B. Jambes
Pour chaque côté :
- `upperleg01`
- `upperleg02`
- `lowerleg01`
- `lowerleg02`
- `foot`

Les os sont suffixés `.L` ou `.R`.

### C. Pieds et orteils
Pour chaque côté :
- `toe1-1` et `toe1-2`
- `toe2-1` à `toe2-3`
- `toe3-1` à `toe3-3`
- `toe4-1` à `toe4-3`
- `toe5-1` à `toe5-3`

### D. Colonne vertébrale et torse
- `spine05`
- `spine04`
- `spine03`
- `spine02`
- `spine01`
- `breast.L`
- `breast.R`

La chaîne vertébrale est reliée à `root` par `spine05`.

### E. Bras et épaules
Pour chaque côté :
- `clavicle`
- `shoulder01`
- `upperarm01`
- `upperarm02`
- `lowerarm01`
- `lowerarm02`
- `wrist`

Les os sont suffixés `.L` ou `.R`.

### F. Mains et doigts
Pour chaque main :
- Cinq chaînes de doigts : `finger1` à `finger5`.
- Trois segments par doigt : `fingerX-1`, `fingerX-2`, `fingerX-3`.
- Os métacarpiens : `metacarpal1` à `metacarpal4`.

Les os sont suffixés `.L` ou `.R`.

### G. Cou et tête
- `neck01`
- `neck02`
- `neck03`
- `head`

### H. Mâchoire et bouche
- `jaw`
- `oris01` à `oris07`, avec les variantes latérales présentes dans le rig.

### I. Langue
- `tongue00`
- `tongue01`
- `tongue02`
- `tongue03`
- `tongue04`
- `tongue05.L` et `tongue05.R`
- `tongue06.L` et `tongue06.R`
- `tongue07.L` et `tongue07.R`

### J. Muscles et expressions faciales
Le rig comporte plusieurs groupes d'os :
- `levator` : structures musculaires faciales.
- `orbicularis` : muscles autour des yeux.
- `risorius` : muscles liés au sourire.
- `temporalis` : structures temporales.
- `oculi` : structures associées aux yeux.
- `special01` à `special06`, avec certaines variantes latérales.

### K. Yeux
- `eye.L`
- `eye.R`

Les yeux disposent également de structures auxiliaires liées à leur animation.

## 3. Hiérarchie générale

La hiérarchie observée dans Blender est organisée autour de plusieurs branches :

- `root`
  - Branche gauche : `pelvis.L` et jambe gauche.
  - Branche droite : `pelvis.R` et jambe droite.
  - Colonne : `spine05` jusqu'à `spine01`.
    - Torse et poitrine.
    - Bras gauche et droit.
    - Cou et tête.
      - Mâchoire, bouche et langue.
      - Yeux et structures faciales.

Les os faciaux sont intégrés à l'armature et reliés à la tête ou à la mâchoire selon leur fonction.

## 4. Architecture d'animation prévue pour MovieStudio

La bibliothèque sera organisée en trois couches indépendantes.

**Couche 1 : Corps**
- Marche et course.
- Déplacements et rotations.
- Gestes des bras et des mains.
- Postures et mouvements du torse.

**Couche 2 : Visage**
- Expressions émotionnelles.
- Sourire et mouvements de bouche.
- Mâchoire et langue.
- Synchronisation labiale.

**Couche 3 : Regard**
- Direction des yeux.
- Orientation de la tête.
- Suivi d'une cible.
- Clignements des yeux.

Ces couches devront pouvoir fonctionner simultanément.

## 5. Principes techniques retenus

1. Le rig MakeHuman `default` constitue notre référence.
2. Les noms et la hiérarchie des os doivent être conservés.
3. Les animations seront enregistrées sous forme d'Actions Blender réutilisables.
4. Les animations corporelles, faciales et du regard devront être indépendantes.
5. Une animation pourra être découpée, ralentie, accélérée, bouclée et enchaînée.
6. Les personnages devront respecter la structure de référence pour bénéficier de la bibliothèque.
7. Le retargeting externe restera facultatif et ne constituera pas le fondement du système.

## 6. Points à vérifier ultérieurement

- Vérifier que les autres personnages MakeHuman utilisent exactement la même structure.
- Vérifier les orientations locales et les axes des os.
- Identifier les éventuels contrôleurs et contraintes disponibles.
- Déterminer les possibilités d'animation faciale avec les os et les Shape Keys.
- Tester la compatibilité des Actions Blender entre plusieurs personnages.

## 7. Décision de conception

**MovieStudio reposera sur un rig MakeHuman de référence unique.**

La priorité est de construire une bibliothèque cohérente d'animations corporelles, d'expressions faciales et de mouvements du regard, directement réutilisables sur les personnages compatibles.

Le rig natif MakeHuman `default` est conservé afin de préserver toutes ses possibilités d'animation, notamment faciales.

---

**Document de référence technique – MovieStudio**