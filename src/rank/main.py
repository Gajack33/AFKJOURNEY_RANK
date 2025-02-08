"""
Point d'entrée principal pour la récupération des classements.
"""

import os
from loguru import logger
import time
from .dreamland import DreamlandRank
from mapper.config_writer import load_mapping

def clear_screen():
    """Nettoie l'écran de la console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    """Affiche le menu principal."""
    clear_screen()
    print("=== Récupération des Classements AFK Journey ===\n")
    print("=== Capture des Classements ===")
    print("1. Royaume Onirique")
    print("2. Arène (à venir)")
    print("3. Arène Suprême (à venir)")
    print("4. Suprématie de Guilde (à venir)")
    print("\n=== Configuration ===")
    print("5. Configurer les positions")
    print("6. Configurer les zones OCR")
    print("\n0. Quitter")
    print("\nVotre choix : ", end='')

def check_configuration(ranking_type: str) -> bool:
    """
    Vérifie si la configuration existe pour un type de classement.
    
    Args:
        ranking_type: Type de classement à vérifier
    
    Returns:
        bool: True si la configuration existe, False sinon
    """
    positions = load_mapping(ranking_type)
    if not positions:
        logger.error(f"Configuration manquante pour {ranking_type}")
        print(f"\nLa configuration des positions pour {ranking_type} n'existe pas.")
        print("Veuillez d'abord configurer les positions via l'option 5 du menu.")
        return False
    return True

def configure_positions():
    """Lance l'outil de configuration des positions."""
    clear_screen()
    print("=== Configuration des Positions ===\n")
    print("1. Royaume Onirique")
    print("2. Arène (à venir)")
    print("3. Arène Suprême (à venir)")
    print("4. Suprématie de Guilde (à venir)")
    print("\n0. Retour")
    
    choice = input("\nVotre choix : ").strip()
    
    if choice == '1':
        clear_screen()
        print("=== Configuration des Positions du Royaume Onirique ===\n")
        print("Pour configurer les positions :")
        print("1. Lancez le jeu et allez à l'écran principal")
        print("2. Exécutez : python -m tests.test_interaction")
        print("3. Suivez les instructions à l'écran")
        input("\nAppuyez sur Entrée pour continuer...")
    elif choice in ['2', '3', '4']:
        print("\nCette fonctionnalité n'est pas encore disponible.")
        input("\nAppuyez sur Entrée pour continuer...")

def configure_ocr():
    """Lance l'outil de configuration des zones OCR."""
    clear_screen()
    print("=== Configuration des Zones OCR ===\n")
    print("Pour configurer les zones OCR :")
    print("1. Capturez d'abord un classement complet")
    print("2. Exécutez : python -m rank.zone_selector")
    print("3. Suivez les instructions à l'écran")
    input("\nAppuyez sur Entrée pour continuer...")

def capture_dreamland():
    """Lance la capture du classement du Royaume Onirique."""
    try:
        # Vérifier la configuration
        if not check_configuration("dreamland"):
            return False
            
        logger.info("Initialisation de la capture du Royaume Onirique...")
        manager = DreamlandRank()
        
        input("\nAppuyez sur Entrée quand le jeu est prêt...")
        
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
        logger.info("Retour au menu principal...")
        for i in range(3):
            manager.click_position("Retour", delay=1.0)
            time.sleep(1.0)
        
        # Extraction et stockage des données
        logger.info("Extraction et stockage des données...")
        players = manager.extract_data()
        if not players:
            logger.error("Échec de l'extraction des données")
            return False
        
        logger.info(f"Données extraites avec succès : {len(players)} joueurs")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la capture : {e}")
        return False

def main():
    """Point d'entrée principal."""
    while True:
        print_menu()
        choice = input().strip()
        
        if choice == '0':
            print("\nAu revoir !")
            break
            
        elif choice == '1':
            clear_screen()
            print("=== Capture du Royaume Onirique ===\n")
            print("Assurez-vous que :")
            print("1. Le jeu est ouvert et en français")
            print("2. La fenêtre du jeu est visible")
            print("3. Vous êtes sur l'écran principal du jeu")
            
            if capture_dreamland():
                print("\nCapture terminée avec succès !")
            else:
                print("\nLa capture a échoué. Consultez les logs pour plus de détails.")
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        elif choice in ['2', '3', '4']:
            print("\nCette fonctionnalité n'est pas encore disponible.")
            input("\nAppuyez sur Entrée pour continuer...")
            
        elif choice == '5':
            configure_positions()
            
        elif choice == '6':
            configure_ocr()
            
        else:
            print("\nChoix invalide.")
            input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main() 