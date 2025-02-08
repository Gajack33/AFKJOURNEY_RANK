# Notes de Réunion

## 22/01/2025 - Mise à jour majeure du Royaume Onirique
### Réalisations
- Implémentation complète de la gestion des dates J et J-1
- Ajout du calcul des moyennes sur 30 jours
- Amélioration de l'affichage des statistiques
- Correction des problèmes de dates dans la base de données

### Points Techniques
- La base de données gère maintenant correctement les dates J et J-1
- Les moyennes sur 30 jours sont calculées avec SQLite
- L'affichage des classements inclut les variations et moyennes

### Prochaines Étapes
- Développer les graphiques de progression
- Implémenter le système d'alertes
- Optimiser les performances OCR
- Préparer l'implémentation des autres classements

## 21/01/2025 - Lancement Initial
### Réalisations
- Mise en place de la structure de base
- Implémentation de la capture du Royaume Onirique
- Création de la base de données
- Développement des commandes Discord de base

### Points Techniques
- Utilisation de win32gui pour la capture d'écran
- Intégration d'EasyOCR pour l'extraction des données
- Structure SQLite pour le stockage
- Bot Discord fonctionnel

### Décisions
- Commencer par le Royaume Onirique
- Utiliser SQLite pour la phase initiale
- Implémenter les fonctionnalités de base en priorité

## Prochaines Réunions
- Planification de l'implémentation des autres classements
- Revue des performances et optimisations
- Discussion sur les fonctionnalités avancées

## 21/01/2024 - Mise à jour majeure
### Réalisations
- Migration réussie vers EasyOCR avec paramètres optimisés
- Implémentation complète du bot Discord avec commandes fonctionnelles
- Amélioration de la capture d'écran avec win32gui
- Correction du défilement avec positions fixes
- Base de données SQLite opérationnelle avec gestion des historiques
- Support des dates (aujourd'hui/hier/spécifique)

### Points Clés
1. OCR et Capture
   - Paramètres OCR optimisés : scale=2.5, contrast=1.5, threshold=240
   - Capture stable avec win32gui
   - Défilement amélioré avec positions fixes

2. Base de Données
   - Structure optimisée pour les classements
   - Gestion efficace des mises à jour
   - Support des historiques joueurs

3. Bot Discord
   - Commandes implémentées :
     - `/royaumeonirique` : classement complet
     - `/royaumeonirique hier:True` : classement d'hier
     - `/royaumeonirique guilde:NomGuilde` : filtrage par guilde
     - `/royaumeonirique joueur:NomJoueur` : historique joueur
   - Formatage amélioré des tableaux
   - Gestion des groupes de 25 joueurs

### Prochaines Étapes
1. Implémentation des autres classements (Arena, Supreme Arena)
2. Développement des graphiques de progression
3. Ajout de statistiques avancées par guilde
4. Mise en place d'un système d'alertes

## 20/01/2024 - Développement Initial
### Points Abordés
- Structure du projet
- Choix des technologies
- Architecture de la base de données
- Planification des fonctionnalités

### Décisions
1. Technologies :
   - Python comme langage principal
   - SQLite pour la base de données
   - EasyOCR pour la reconnaissance de texte
   - Discord.py pour le bot

2. Architecture :
   - Structure modulaire
   - Séparation claire des responsabilités
   - Tests unitaires importants

3. Priorités :
   - Focus initial sur le Royaume Onirique
   - Validation du concept avant extension
   - Tests approfondis de l'OCR

### Actions
- ✓ Mise en place de la structure du projet
- ✓ Configuration de l'environnement de développement
- ✓ Création des classes de base
- ✓ Tests initiaux de capture d'écran

## 21/01/2024 - Développement OCR et Base de Données
### Réalisations
- Migration réussie vers EasyOCR
- Optimisation des paramètres OCR :
  - Échelle : 2.5
  - Contraste : 1.5
  - Luminosité : 0
  - Seuil : 240
- Implémentation de la base de données SQLite
- Gestion des doublons dans les classements
- Correction de la dérive du défilement

### Problèmes Résolus
- Capture d'écran sur écran secondaire
- Précision de l'OCR pour les rangs et scores
- Dérive du défilement avec correction progressive
- Contraintes d'unicité dans la base de données

### Prochaines Étapes
- Intégration Discord
- Support des autres classements
- Visualisation des données
- Tests de robustesse

## 21/01/2024 - Développement OCR et Automatisation
### Réalisations
- Optimisation de la capture d'écran avec support multi-écrans
- Implémentation du défilement par drag & drop (500 pixels)
- Configuration d'EasyOCR avec paramètres optimaux :
  - Échelle : 2.5
  - Contraste : 1.5
  - Luminosité : 0
  - Seuil : 240
- Extraction réussie des données du Royaume Onirique :
  - Dates (J-1, J-2)
  - Rangs
  - Noms des joueurs
  - Guildes
  - Scores

### Prochaines Étapes
1. Implémentation du stockage des données
2. Extension aux autres types de classements
3. Développement des visualisations
4. Intégration Discord

### Points d'Attention
- Maintenir la qualité d'extraction pour les autres classements
- Optimiser le stockage pour les données historiques
- Assurer la fiabilité du système sur de longues périodes

## Session du 21/01/2024 - Tests d'Interaction avec le Jeu

### Problèmes Rencontrés et Solutions
1. **Déplacement de la Souris**
   - Problème initial avec les coordonnées négatives sur écran secondaire
   - Tentative de normalisation des coordonnées qui a compliqué le problème
   - Solution finale : utilisation directe de `ctypes.windll.user32.SetCursorPos`

2. **Clics dans le Jeu**
   - Tests avec différentes méthodes :
     - `mouse_event`
     - `SendMessage`
     - `PyAutoGUI`
   - Implémentation d'un déplacement progressif de la souris
   - Ajout de délais entre les actions pour plus de fiabilité

3. **Interface de Test**
   - Création d'une application de test avec tkinter
   - Fonctionnalités implémentées :
     - Sélection de la fenêtre du jeu
     - Test de déplacement au centre
     - Affichage des coordonnées du curseur
     - Test de clics à des coordonnées spécifiques
     - Choix de la méthode de clic

### Leçons Apprises
1. Les coordonnées négatives sur écran secondaire nécessitent une gestion spéciale
2. Le déplacement progressif de la souris est plus fiable qu'un déplacement direct
3. L'activation de la fenêtre avant interaction est cruciale
4. Les délais entre les actions sont nécessaires pour la fiabilité

### Prochaines Étapes
1. Intégrer ces méthodes d'interaction dans le script principal
2. Tester la fiabilité sur différentes configurations d'écran
3. Optimiser les délais entre les actions
4. Ajouter des mécanismes de vérification pour confirmer que les clics sont bien effectués
