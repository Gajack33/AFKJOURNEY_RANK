# API Reference: test_dreamland.py

## Classes

### `DreamlandRank`

Gestionnaire principal pour la capture et le stockage des données du Royaume Onirique.

#### Méthodes

##### `__init__(self)`
Initialise le gestionnaire avec les configurations nécessaires.
- Charge les positions depuis `dreamland.json`
- Initialise EasyOCR
- Configure la base de données

##### `navigate_to_ranking(self) -> bool`
Navigation automatique vers le classement.
- **Retourne**: `True` si la navigation réussit, `False` sinon

##### `scroll_and_capture(self, num_scrolls: int = 24) -> bool`
Capture les données en faisant défiler la liste.
- **Paramètres**:
  - `num_scrolls`: Nombre de défilements à effectuer
- **Retourne**: `True` si la capture réussit, `False` sinon

##### `extract_data(self) -> list[dict]`
Extrait les données des captures via OCR.
- **Retourne**: Liste de dictionnaires contenant les données des joueurs
  ```python
  [
    {
      'rank': int,
      'name': str,
      'guild': str,
      'score': str
    },
    ...
  ]
  ```

## Fonctions

### `return_to_main_menu(manager: DreamlandRank) -> bool`
Retourne au menu principal après la capture.
- **Paramètres**:
  - `manager`: Instance de DreamlandRank
- **Retourne**: `True` si le retour réussit, `False` sinon

### `test_dreamland() -> bool`
Fonction principale de test.
- **Retourne**: `True` si le test réussit, `False` sinon

## Utilisation

```python
from tests.test_dreamland import test_dreamland

# Exécution du test complet
success = test_dreamland()

# Utilisation manuelle des composants
from tests.test_dreamland import DreamlandRank

manager = DreamlandRank()
if manager.navigate_to_ranking():
    if manager.scroll_and_capture(num_scrolls=24):
        players = manager.extract_data()
        return_to_main_menu(manager)
```

## Événements et Logs

Le module utilise `loguru` pour les logs avec les niveaux suivants :
- `logger.info()`: Étapes principales du processus
- `logger.debug()`: Détails d'exécution
- `logger.warning()`: Problèmes non critiques
- `logger.error()`: Erreurs bloquantes

## Dépendances

- `loguru`: Gestion des logs
- `easyocr`: OCR pour l'extraction de texte
- `cv2`: Traitement d'images
- `numpy`: Manipulation de données
- `sqlite3`: Stockage en base de données

## Configuration

### Fichiers requis

```
resources/
├── config/
│   └── ocr_zones.json     # Zones d'extraction OCR
└── data/
    └── mapping/
        └── dreamland.json # Positions des boutons
```

### Format de ocr_zones.json
```json
{
  "rank": [
    {
      "x_percent": float,
      "y_percent": float,
      "width_percent": float,
      "height_percent": float
    }
  ],
  "name": [...],
  "guild": [...],
  "score": [...]
}
```

### Format de dreamland.json
```json
{
  "positions": {
    "Mode": {"x": int, "y": int},
    "EntrerRoyaumeOnirique": {"x": int, "y": int},
    "EntrerClassementOnirique": {"x": int, "y": int},
    "J-1": {"x": int, "y": int},
    "Retour": {"x": int, "y": int}
  }
}
``` 