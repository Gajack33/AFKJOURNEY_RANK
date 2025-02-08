"""
Module de gestion des configurations de mapping.
"""

import json
import os
from datetime import datetime
import shutil
from loguru import logger

# Chemin racine du projet
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

def save_mapping(ranking_type, positions):
    """
    Sauvegarde la configuration des positions pour un type de classement.
    
    Args:
        ranking_type (str): Type de classement (dreamland, arena, supreme_arena, guild)
        positions (dict): Dictionnaire des positions à sauvegarder
    """
    config_dir = os.path.join(ROOT_DIR, "resources", "data", "mapping")
    config_path = os.path.join(config_dir, f"{ranking_type}.json")
    
    # Créer le dossier s'il n'existe pas
    os.makedirs(config_dir, exist_ok=True)
    
    # Créer une sauvegarde si le fichier existe déjà
    if os.path.exists(config_path):
        backup_dir = os.path.join(config_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"{ranking_type}_{timestamp}.json")
        
        shutil.copy2(config_path, backup_path)
        logger.info(f"Sauvegarde créée : {backup_path}")
    
    # Créer la nouvelle configuration
    config = {
        "metadata": {
            "ranking_type": ranking_type,
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0"
        },
        "positions": positions
    }
    
    # Sauvegarder la nouvelle configuration
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Configuration sauvegardée : {config_path}")

def load_mapping(ranking_type):
    """
    Charge la configuration des positions pour un type de classement.
    
    Args:
        ranking_type (str): Type de classement (dreamland, arena, supreme_arena, guild)
        
    Returns:
        dict: Configuration chargée ou {} si non trouvée
    """
    config_path = os.path.join(ROOT_DIR, "resources", "data", "mapping", f"{ranking_type}.json")
    
    if not os.path.exists(config_path):
        logger.warning(f"Aucune configuration trouvée pour {ranking_type}")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Configuration chargée pour {ranking_type}")
        return config.get("positions", {})
    
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration : {e}")
        return {}

def validate_mapping(positions):
    """
    Valide une configuration de positions.
    
    Args:
        positions (dict): Configuration à valider
        
    Returns:
        tuple: (bool, str) - (valide, message d'erreur)
    """
    if not positions:
        return False, "La configuration est vide"
    
    required_fields = {"x", "y"}
    
    for name, pos in positions.items():
        if not isinstance(pos, dict):
            return False, f"Position invalide pour {name}"
        
        missing_fields = required_fields - set(pos.keys())
        if missing_fields:
            return False, f"Champs manquants pour {name}: {missing_fields}"
        
        if not all(isinstance(pos[field], (int, float)) for field in required_fields):
            return False, f"Types invalides pour {name}"
    
    return True, "Configuration valide" 