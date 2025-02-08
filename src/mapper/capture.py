"""
Module de capture d'écran pour l'application de mapping.
"""

import cv2
import numpy as np
import pyautogui
from loguru import logger
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import time

def get_window_list():
    """
    Récupère la liste des fenêtres visibles.
    
    Returns:
        list: Liste de tuples (hwnd, titre) des fenêtres visibles
    """
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "AFK Journey" in title:  # Ne garder que la fenêtre du jeu
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                window_info = f"{title} ({width}x{height})"
                windows.append((hwnd, window_info))
                logger.debug(f"Fenêtre trouvée : {window_info}")
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return sorted(windows, key=lambda x: x[1].lower())

def find_game_windows():
    """
    Trouve toutes les fenêtres du jeu AFK Journey.
    
    Returns:
        list: Liste de tuples (hwnd, titre) des fenêtres du jeu
    """
    return get_window_list()

def bring_window_to_front(hwnd):
    """
    Amène la fenêtre au premier plan.
    
    Args:
        hwnd: Handle de la fenêtre
    """
    try:
        # Vérifier si la fenêtre est minimisée
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # Mettre la fenêtre au premier plan
        win32gui.SetForegroundWindow(hwnd)
        
        # Attendre un court instant pour que la fenêtre soit bien au premier plan
        time.sleep(0.5)
    except Exception as e:
        logger.error(f"Erreur lors de la mise au premier plan : {e}")

def get_window_info(hwnd):
    """
    Obtient les informations de la fenêtre.
    
    Args:
        hwnd: Handle de la fenêtre
        
    Returns:
        tuple: (left, top, width, height, client_left, client_top, client_width, client_height)
    """
    try:
        # Obtenir les dimensions de la fenêtre
        window_rect = win32gui.GetWindowRect(hwnd)
        client_rect = win32gui.GetClientRect(hwnd)
        
        # Convertir les coordonnées client en coordonnées écran
        client_left, client_top = win32gui.ClientToScreen(hwnd, (0, 0))
        
        left, top, right, bottom = window_rect
        client_width = client_rect[2] - client_rect[0]
        client_height = client_rect[3] - client_rect[1]
        
        return (left, top, right - left, bottom - top,
                client_left, client_top, client_width, client_height)
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention des informations de la fenêtre : {e}")
        return None

def capture_window(hwnd=None):
    """
    Capture l'écran de la fenêtre spécifiée.
    
    Args:
        hwnd: Handle de la fenêtre à capturer
        
    Returns:
        numpy.ndarray: Image capturée ou None en cas d'erreur
    """
    try:
        if hwnd is None:
            logger.warning("Aucune fenêtre spécifiée pour la capture")
            return None
        
        # Mettre la fenêtre au premier plan
        bring_window_to_front(hwnd)
        
        # Obtenir les dimensions de la fenêtre
        window_rect = win32gui.GetWindowRect(hwnd)
        
        # Capturer la zone de la fenêtre
        screenshot = pyautogui.screenshot(region=(
            window_rect[0],  # Left
            window_rect[1],  # Top
            window_rect[2] - window_rect[0],  # Width
            window_rect[3] - window_rect[1]   # Height
        ))
        
        # Convertir en format OpenCV
        img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Redimensionner à la résolution cible
        return resize_to_resolution(img_cv)
    
    except Exception as e:
        logger.error(f"Erreur lors de la capture : {e}")
        return None

def resize_to_resolution(image, target_width=750, target_height=1334):
    """
    Redimensionne l'image à la résolution cible.
    
    Args:
        image (numpy.ndarray): Image à redimensionner
        target_width (int): Largeur cible
        target_height (int): Hauteur cible
        
    Returns:
        numpy.ndarray: Image redimensionnée
    """
    if image is None:
        return None
    
    # Calculer le ratio pour conserver les proportions
    current_ratio = image.shape[1] / image.shape[0]
    target_ratio = target_width / target_height
    
    if current_ratio > target_ratio:
        # Image plus large que la cible
        new_width = target_width
        new_height = int(target_width / current_ratio)
    else:
        # Image plus haute que la cible
        new_height = target_height
        new_width = int(target_height * current_ratio)
    
    # Redimensionner l'image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Créer une image noire de la taille cible
    result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    
    # Calculer les positions pour centrer l'image
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    # Placer l'image redimensionnée au centre
    result[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
    
    return result 