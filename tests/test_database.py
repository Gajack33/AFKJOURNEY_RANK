"""
Test de l'initialisation de la base de données.
"""

import os
import sys
from loguru import logger

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rank.database import RankDatabase

def test_database_init():
    """Test l'initialisation de la base de données."""
    try:
        # Initialiser la base de données
        logger.info("Initialisation de la base de données...")
        db = RankDatabase()
        
        # Vérifier que le fichier existe
        if os.path.exists(db.db_path):
            logger.info(f"Base de données créée avec succès : {db.db_path}")
            return True
        else:
            logger.error("La base de données n'a pas été créée")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données : {e}")
        return False

if __name__ == "__main__":
    logger.info("Test d'initialisation de la base de données...")
    if test_database_init():
        logger.info("Test réussi !")
    else:
        logger.error("Test échoué.") 