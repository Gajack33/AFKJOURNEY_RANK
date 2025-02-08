# Guide de Test du Royaume Onirique

Ce guide explique comment utiliser et comprendre le script de test `test_dreamland.py` qui permet de capturer et stocker automatiquement les données du classement du Royaume Onirique.

## Vue d'ensemble

Le script `test_dreamland.py` est un outil de test qui :
1. Navigue automatiquement vers le classement du Royaume Onirique
2. Capture les données en faisant défiler la liste
3. Extrait les informations via OCR
4. Stocke les données dans la base de données SQLite

## Prérequis

- Le jeu doit être ouvert et en français
- La fenêtre du jeu doit être visible et non minimisée
- Les positions de mapping doivent être configurées (`resources/data/mapping/dreamland.json`)
- Les zones OCR doivent être configurées (`resources/config/ocr_zones.json`)

## Utilisation

1. Ouvrir le jeu et se connecter
2. Ouvrir un terminal dans le dossier du projet
3. Exécuter la commande :
```bash
python -m tests.test_dreamland
```
4. Appuyer sur Entrée quand demandé pour démarrer le test

## Processus détaillé

### 1. Navigation
- Clic sur le bouton "Mode"
- Clic sur "Entrer dans le Royaume Onirique"
- Clic sur "Entrer dans le Classement"

### 2. Capture des données
- Clic sur "J-1" pour afficher le classement d'hier
- Capture de l'écran initial
- 24 défilements avec captures d'écran
- Les captures sont sauvegardées dans `resources/data/captures/`

### 3. Extraction OCR
- Utilisation d'EasyOCR pour extraire :
  - Rangs
  - Noms des joueurs
  - Noms des guildes
  - Scores
- Les zones d'extraction sont définies dans `ocr_zones.json`

### 4. Stockage des données
- Les données sont stockées dans la base SQLite
- Tables utilisées :
  - `ranking_dates` : Dates des classements
  - `players` : Informations des joueurs
  - `rankings` : Positions et scores

## Résolution des problèmes

### Erreur de navigation
- Vérifier que le jeu est bien ouvert et visible
- Vérifier les positions dans `dreamland.json`
- Relancer le test

### Erreur d'OCR
- Vérifier les zones dans `ocr_zones.json`
- Vérifier que les captures sont nettes
- Vérifier que le texte est bien visible

### Erreur de base de données
- Vérifier les permissions du dossier `resources/data/database/`
- Vérifier l'espace disque disponible

## Fichiers de sortie

### Captures d'écran
```
resources/data/captures/
├── dreamland_capture_YYYYMMDD_HHMMSS_1.png
├── dreamland_capture_YYYYMMDD_HHMMSS_2.png
└── ...
```

### Base de données
```
resources/data/database/rankings.db
```

## Logs et débogage

Les logs sont affichés dans la console avec différents niveaux :
- INFO : Informations sur le processus
- DEBUG : Détails techniques
- WARNING : Problèmes mineurs
- ERROR : Erreurs bloquantes

## Configuration avancée

### Modification du nombre de défilements
Dans `test_dreamland.py` :
```python
if not manager.scroll_and_capture(num_scrolls=24):  # Modifier cette valeur
```

### Modification des délais
Dans `dreamland.py` :
```python
self.click_position("Position", delay=1.0)  # Modifier les délais
``` 