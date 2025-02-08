"""
Test du processus complet de capture et stockage des données du Royaume Onirique.
"""

import os
import sys
from loguru import logger
import time

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rank.dreamland import DreamlandRank

def return_to_main_menu(manager):
    """Retourne au menu principal."""
    logger.info("Retour au menu principal")
    
    # Cliquer sur Retour trois fois avec délai
    for i in range(3):
        manager.click_position("Retour", delay=1.0)
        logger.info(f"Retour {i+1}/3 effectué")
        time.sleep(1.0)
    
    return True

def test_dreamland():
    """Test le processus complet pour le Royaume Onirique."""
    try:
        # Initialiser le gestionnaire
        logger.info("Initialisation du gestionnaire DreamlandRank")
        manager = DreamlandRank()
        
        # Navigation vers le classement
        logger.info("Navigation vers le classement...")
        if not manager.navigate_to_ranking():
            logger.error("Échec de la navigation")
            return False
        
        # Capture des données
        logger.info("Capture des données...")
        if not manager.scroll_and_capture(num_scrolls=24):
            logger.error("Échec de la capture")
            return False
            
        # Retour au menu principal
        if not return_to_main_menu(manager):
            logger.error("Échec du retour au menu principal")
            return False
        
        # Extraction et stockage des données
        logger.info("Extraction et stockage des données...")
        players = manager.extract_data()
        if not players:
            logger.error("Échec de l'extraction des données")
            return False
        
        logger.info(f"Données extraites avec succès : {len(players)} joueurs")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors du test : {e}")
        return False

if __name__ == "__main__":
    logger.info("Début du test...")
    input("Appuyez sur Entrée pour commencer le test...")
    
    if test_dreamland():
        logger.info("Test réussi !")
    else:
        logger.error("Test échoué.") 