"""
Module de base pour la gestion des classements.
"""

import time
from loguru import logger
import pyautogui
import cv2
import numpy as np
import win32gui
import win32ui
import win32con

from mapper.capture import capture_window, find_game_windows
from mapper.config_writer import load_mapping

class RankBase:
    """Classe de base pour la gestion des classements."""
    
    def __init__(self, ranking_type):
        """
        Initialise un gestionnaire de classement.
        
        Args:
            ranking_type (str): Type de classement (dreamland, arena, supreme_arena, guild)
        """
        self.ranking_type = ranking_type
        self.positions = load_mapping(ranking_type)
        self.hwnd = None
        self.current_image = None
        
        if not self.positions:
            raise ValueError(f"Aucune position configurée pour {ranking_type}")
    
    def find_game_window(self):
        """Trouve la fenêtre du jeu."""
        windows = find_game_windows()
        if not windows:
            raise RuntimeError("Aucune fenêtre de jeu trouvée")
        
        # Prendre la première fenêtre trouvée
        self.hwnd = windows[0][0]
        logger.info(f"Fenêtre de jeu trouvée : {windows[0][1]}")
        return True
    
    def capture_screen(self):
        """Capture l'écran du jeu."""
        try:
            if not self.hwnd:
                logger.error("Fenêtre du jeu non trouvée")
                return False

            # Activer la fenêtre
            self._activate_window()
            time.sleep(0.2)  # Attendre que la fenêtre soit active

            # Faire la capture avec la fonction qui marchait
            img = capture_window(self.hwnd)
            if img is None:
                logger.error("Échec de la capture d'écran")
                return False

            # Vérifier que l'image n'est pas noire
            if img.mean() < 5:  # Si l'image est presque noire
                logger.error("La capture est noire")
                return False

            self.current_image = img
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la capture : {e}")
            return False
    
    def _activate_window(self):
        """Active la fenêtre du jeu."""
        if not self.hwnd:
            raise RuntimeError("Fenêtre de jeu non trouvée")
            
        # Vérifier si la fenêtre n'est pas déjà active
        if win32gui.GetForegroundWindow() != self.hwnd:
            # Activer la fenêtre
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.5)  # Attendre que la fenêtre soit active
            logger.debug("Fenêtre du jeu activée")
        
        return True

    def click_position(self, position_name, delay=1.0):
        """
        Clique sur une position configurée.
        
        Args:
            position_name (str): Nom de la position
            delay (float): Délai après le clic en secondes
        """
        if position_name not in self.positions:
            raise ValueError(f"Position '{position_name}' non trouvée")
        
        # Activer la fenêtre avant le clic
        self._activate_window()
        
        pos = self.positions[position_name]
        x, y = pos["x"], pos["y"]
        
        # Convertir les coordonnées relatives en coordonnées écran
        screen_x, screen_y = self._get_screen_coordinates(x, y)
        
        # Cliquer et attendre
        pyautogui.click(screen_x, screen_y)
        time.sleep(delay)
        logger.debug(f"Clic sur {position_name} ({screen_x}, {screen_y})")
    
    def _get_screen_coordinates(self, x, y):
        """
        Convertit les coordonnées relatives en coordonnées écran.
        
        Args:
            x (int): Coordonnée X relative
            y (int): Coordonnée Y relative
            
        Returns:
            tuple: (x, y) coordonnées écran
        """
        if not self.hwnd:
            raise RuntimeError("Fenêtre de jeu non trouvée")
            
        # Obtenir le point (0,0) de la zone client en coordonnées écran
        client_origin = win32gui.ClientToScreen(self.hwnd, (0, 0))
        
        # Ajouter les coordonnées relatives
        screen_x = client_origin[0] + x
        screen_y = client_origin[1] + y
        
        logger.debug(f"Conversion coordonnées : ({x}, {y}) -> ({screen_x}, {screen_y})")
        logger.debug(f"Origine client : {client_origin}")
        
        return screen_x, screen_y
    
    def navigate_to_ranking(self):
        """
        Navigue jusqu'au classement.
        À implémenter dans les classes dérivées.
        """
        raise NotImplementedError
    
    def scroll_and_capture(self):
        """
        Fait défiler le classement et capture les données.
        À implémenter dans les classes dérivées.
        """
        raise NotImplementedError
    
    def extract_data(self):
        """
        Extrait les données du classement.
        À implémenter dans les classes dérivées.
        """
        raise NotImplementedError 