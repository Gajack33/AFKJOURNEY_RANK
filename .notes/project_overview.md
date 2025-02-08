# Vue d'Ensemble du Projet

## Objectif
Automatiser la capture et le suivi des classements du Royaume Onirique, avec un focus sur l'historique des joueurs et les statistiques de progression.

## Fonctionnalités Principales

### Capture Automatique
- Capture d'écran automatisée du Royaume Onirique
- Extraction des données via OCR (EasyOCR)
- Gestion automatique des dates (J-1)
- Traitement et validation des données

### Base de Données
- Stockage structuré des classements
- Suivi des dates J et J-1
- Calcul des moyennes sur 30 jours
- Historique complet des variations

### Interface Discord
- Commande `/royaumeonirique joueur:[nom]`
- Affichage des classements actuels
- Historique des positions
- Statistiques de progression

## État Actuel
- ✅ Capture automatique fonctionnelle
- ✅ Stockage en base de données optimisé
- ✅ Commandes Discord de base
- ✅ Calcul des moyennes sur 30 jours
- ✅ Gestion des dates J/J-1

## Prochaines Étapes
- 📋 Graphiques de progression
- 📋 Système d'alertes
- 📋 Optimisation des performances
- 📋 Extension à d'autres classements

## Technologies Utilisées
- Python 3.8+
- SQLite
- Discord.py
- EasyOCR
- win32gui

## Notes Techniques
- La capture est effectuée quotidiennement
- Les données sont validées avant stockage
- Les moyennes sont calculées en temps réel
- L'interface est optimisée pour la lisibilité