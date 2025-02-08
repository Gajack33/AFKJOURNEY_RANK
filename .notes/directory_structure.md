# Structure du Projet AFKJOURNEY_RANK

```
afkjourney_rank/
├── src/                    # Code source principal
│   ├── bot/               # Bot Discord
│   │   ├── __init__.py   # Initialisation du package bot
│   │   ├── discord_bot.py # Point d'entrée du bot
│   │   ├── commands.py   # Gestionnaire des commandes
│   │   ├── config.py     # Configuration du bot
│   │   └── embeds.py     # Générateur d'embeds Discord
│   ├── mapper/           # Système de mapping
│   │   ├── __init__.py   # Initialisation du package mapper
│   │   ├── capture.py    # Capture d'écran
│   │   └── config_writer.py # Gestion des configurations
│   └── rank/             # Système de classement
│       ├── __init__.py   # Initialisation du package rank
│       ├── base.py       # Classe de base pour les classements
│       ├── database.py   # Gestion de la base de données
│       ├── dreamland.py  # Classement du Royaume Onirique
│       └── zone_selector.py # Sélection des zones OCR
├── tests/                 # Tests unitaires et d'intégration
│   ├── test_database.py  # Tests de la base de données
│   ├── test_dreamland.py # Tests du Royaume Onirique
│   └── test_interaction.py # Tests d'interaction
├── resources/            # Ressources du projet
│   ├── config/          # Fichiers de configuration
│   │   ├── config.yaml  # Configuration générale
│   │   ├── discord.yaml # Configuration Discord
│   │   └── ocr_zones.json # Zones OCR
│   └── data/           # Données
│       ├── database/   # Base de données SQLite
│       ├── mapping/    # Données de mapping
│       └── captures/   # Captures d'écran
├── docs/                # Documentation
├── .env.example        # Template des variables d'environnement
├── .env               # Variables d'environnement
├── README.md         # Documentation principale
└── requirements.txt  # Dépendances Python
```

## Description des Changements

### Principaux changements

1. **Réorganisation du Code Source**
   - Tout le code source est maintenant dans le dossier `src/`
   - Séparation claire entre bot, mapper et rank
   - Meilleure organisation des modules

2. **Gestion des Ressources**
   - Nouveau dossier `resources/` qui centralise toutes les ressources
   - Configuration dans `resources/config/`
   - Données dans `resources/data/`
   - Base de données SQLite dans `resources/data/database/`

3. **Tests**
   - Tests unitaires et d'intégration dans `tests/`
   - Tests spécifiques pour chaque composant
   - Test d'interaction pour la configuration des zones OCR

4. **Documentation**
   - Documentation principale dans `README.md`
   - Documentation détaillée à venir dans `docs/`

### Migration Effectuée

1. ✅ Déplacement des modules vers `src/`
2. ✅ Consolidation des fichiers de configuration dans `resources/config/`
3. ✅ Déplacement des données vers `resources/data/`
4. ✅ Mise en place de la base de données SQLite
5. ✅ Configuration des zones OCR