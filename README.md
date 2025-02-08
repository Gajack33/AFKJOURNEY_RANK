# AFK Journey Rank Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Application de suivi automatisé des classements de jeu avec intégration Discord.

## Fonctionnalités

- Suivi automatique des classements :
  - Royaume Onirique
  - Arène (à venir)
  - Arène Suprême (à venir)
  - Suprématie de Guilde (à venir)
- Capture et analyse automatique des données
- Stockage des historiques dans SQLite
- Bot Discord avec commandes interactives
- Visualisations et statistiques de progression

## Prérequis

- Python 3.8+
- Tesseract OCR
- SQLite
- Dépendances Python (voir requirements.txt)

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-username/AFKJOURNEY_RANK.git
cd AFKJOURNEY_RANK
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances Python :
```bash
pip install -r requirements.txt
```

4. Installer Tesseract OCR :
- Windows : Télécharger et installer depuis [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux : `sudo apt-get install tesseract-ocr`

5. Configurer l'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos configurations

cp resources/config/discord.yaml.example resources/config/discord.yaml
# Éditer discord.yaml avec vos configurations
```

## Configuration

1. Configurer les zones OCR :
```bash
python -m tests.test_interaction
```

2. Configurer le bot Discord dans `resources/config/discord.yaml`

## Utilisation

### Capture des Classements
```bash
cd src
python -m rank.main
```
Suivez le menu interactif pour choisir le classement à capturer.

### Bot Discord
```bash
cd src
python -m bot.discord_bot
```

### Commandes Discord

- `/royaumeonirique [joueur] [guilde] [date] [hier]` : Affiche le classement du Royaume Onirique
  - `joueur` : Nom du joueur à rechercher (optionnel)
  - `guilde` : Nom de la guilde à filtrer (optionnel)
  - `date` : Date spécifique au format JJ/MM/YY (optionnel)
  - `hier` : Afficher le classement d'hier (optionnel)
- `/progression joueur` : Affiche un graphique de progression sur 10 jours

## Structure du Projet

```
afkjourney_rank/
├── src/                    # Code source principal
│   ├── bot/               # Bot Discord
│   ├── mapper/           # Système de mapping
│   └── rank/             # Système de classement
├── tests/                 # Tests unitaires et d'intégration
├── resources/            # Ressources du projet
│   ├── config/          # Fichiers de configuration
│   └── data/           # Données
│       ├── database/   # Base de données SQLite
│       ├── mapping/    # Données de mapping
│       └── captures/   # Captures d'écran
├── docs/                # Documentation
├── .env.example        # Template des variables d'environnement
└── requirements.txt    # Dépendances Python
```

## Développement

### Tests
```bash
python -m pytest tests/
```

### Style de code
Le projet suit le style de code [Black](https://github.com/psf/black). Pour formater le code :
```bash
black .
```

### Base de données
La base de données SQLite est automatiquement créée dans `resources/data/database/rankings.db`

## Contribution

Les contributions sont les bienvenues ! Veuillez consulter [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.