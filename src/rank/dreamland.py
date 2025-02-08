"""
Module de gestion du classement du Royaume Onirique.
"""

from loguru import logger
import time
import pyautogui
import win32con
import win32api
import ctypes
from ctypes import wintypes
import os
from dotenv import load_dotenv
import cv2
import win32gui
from PIL import Image
import numpy as np
import re
import json
import easyocr
from .database import RankDatabase
from datetime import datetime, timedelta

# Charger les variables d'environnement
load_dotenv()

from .base import RankBase

# Initialiser EasyOCR (ne sera initialisé qu'une seule fois)
reader = easyocr.Reader(['en'])

# Structures pour SendInput
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]

class INPUT_union(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_union)
    ]

class DreamlandRank(RankBase):
    """Gestionnaire du classement du Royaume Onirique."""
    
    def __init__(self):
        """Initialise le gestionnaire du Royaume Onirique."""
        super().__init__("dreamland")
        
        # Initialiser EasyOCR
        self.reader = easyocr.Reader(['en'])
        
        # Initialiser la base de données
        self.db = RankDatabase()
        
        # Vérifier que toutes les positions nécessaires sont configurées
        required_positions = {
            "Mode",
            "EntrerRoyaumeOnirique",
            "EntrerClassementOnirique",
            "J-1",
            "Retour"
        }
        
        missing = required_positions - set(self.positions.keys())
        if missing:
            raise ValueError(f"Positions manquantes : {missing}")
    
    def _send_key(self, key):
        """
        Envoie une touche en utilisant SendInput.
        
        Args:
            key (str): Touche à envoyer (un seul caractère)
        """
        if not self.hwnd:
            return False
            
        # Convertir le caractère en code virtuel
        vk = win32api.VkKeyScan(key) & 0xFF
        
        # Créer les structures pour SendInput
        inputs = (INPUT * 2)()
        
        # Keydown
        inputs[0].type = 1  # INPUT_KEYBOARD
        inputs[0].union.ki.wVk = vk
        inputs[0].union.ki.dwFlags = 0
        
        # Keyup
        inputs[1].type = 1  # INPUT_KEYBOARD
        inputs[1].union.ki.wVk = vk
        inputs[1].union.ki.dwFlags = 2  # KEYEVENTF_KEYUP
        
        # Envoyer l'input
        self._activate_window()
        time.sleep(0.1)
        ctypes.windll.user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
        time.sleep(0.1)
        
        logger.debug(f"Touche '{key}' envoyée via SendInput")
        return True
    
    def navigate_to_ranking(self):
        """Navigue jusqu'au classement du Royaume Onirique."""
        try:
            # S'assurer que la fenêtre est trouvée
            if not self.find_game_window():
                logger.error("Impossible de trouver la fenêtre du jeu")
                return False
            
            # Activer la fenêtre
            self._activate_window()
            time.sleep(1.0)  # Attendre que la fenêtre soit active
            logger.info("Fenêtre activée, début de la navigation")
            
            # Cliquer sur le bouton Mode pour ouvrir le menu
            logger.info("Clic sur Mode")
            self.click_position("Mode", delay=3.0)
            
            # Entrer dans le Royaume Onirique
            logger.info("Clic sur EntrerRoyaumeOnirique")
            self.click_position("EntrerRoyaumeOnirique", delay=3.0)
            
            # Entrer dans le classement
            logger.info("Clic sur EntrerClassementOnirique")
            self.click_position("EntrerClassementOnirique", delay=3.0)
            
            logger.info("Navigation vers le classement du Royaume Onirique réussie")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la navigation : {e}")
            return False
    
    def drag_mouse(self, start_x, start_y, end_x, end_y, duration=0.5):
        """
        Simule un glissement de souris d'un point à un autre.
        
        Args:
            start_x (int): Position X de départ
            start_y (int): Position Y de départ
            end_x (int): Position X d'arrivée
            end_y (int): Position Y d'arrivée
            duration (float): Durée du glissement en secondes
        """
        # Déplacer la souris au point de départ
        pyautogui.moveTo(start_x, start_y)
        time.sleep(0.1)
        
        # Appuyer sur le bouton gauche
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        
        # Déplacer progressivement la souris
        steps = 20
        for i in range(steps + 1):
            x = start_x + ((end_x - start_x) * i // steps)
            y = start_y + ((end_y - start_y) * i // steps)
            pyautogui.moveTo(x, y)
            time.sleep(duration / steps)
        
        # Relâcher le bouton gauche
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.1)

    def scroll_and_capture(self, num_scrolls=24):
        """
        Fait défiler le classement et capture les données.
        
        Args:
            num_scrolls (int): Nombre de défilements à effectuer
        """
        try:
            # Toujours cliquer sur J-1 avant de commencer
            self.click_position("J-1", delay=1.0)
            
            # Liste pour stocker toutes les captures
            self.captures = []
            
            # Capturer l'écran initial
            if not self.capture_screen():
                return False
            self.captures.append(self.current_image.copy())
            
            # Points fixes pour le défilement (coordonnées relatives à la fenêtre)
            scroll_start_y = 1000  # Point de départ fixe
            scroll_end_y = 500     # Point d'arrivée initial
            scroll_x = 375         # Position X fixe
            
            # Faire défiler et capturer
            for i in range(num_scrolls):
                # Réduire progressivement le point d'arrivée
                current_end_y = scroll_end_y - (i * 0.20)  # Réduit de 0.5 pixels à chaque itération
                
                # Convertir les coordonnées relatives en coordonnées écran
                screen_x, screen_start_y = self._get_screen_coordinates(scroll_x, scroll_start_y)
                _, screen_end_y = self._get_screen_coordinates(scroll_x, current_end_y)
                
                # Faire glisser de bas en haut
                self.drag_mouse(screen_x, screen_start_y, screen_x, screen_end_y, duration=0.5)
                time.sleep(2)
                
                # Capturer l'écran
                if not self.capture_screen():
                    return False
                self.captures.append(self.current_image.copy())
                
                logger.info(f"Capture {i+1}/{num_scrolls} effectuée (point d'arrivée : {current_end_y})")
            
            # Sauvegarder toutes les captures
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'data', 'captures')
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            for idx, img in enumerate(self.captures):
                output_path = os.path.join(output_dir, f'dreamland_capture_{timestamp}_{idx+1}.png')
                cv2.imwrite(output_path, img)
                logger.info(f"Capture {idx+1} sauvegardée : {output_path}")
            
            logger.info("Capture des données du Royaume Onirique terminée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la capture : {e}")
            return False

    def _extract_region(self, image, region, is_rank=False, is_score=False):
        """Extrait le texte d'une région spécifique de l'image"""
        try:
            x, y, w, h = region
            roi = image[y:y+h, x:x+w].copy()
            
            # Redimensionner avec un facteur de 2.5
            h, w = roi.shape[:2]
            scale = 2.5
            roi = cv2.resize(roi, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
            
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Ajuster le contraste (1.5) et la luminosité (0)
            gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
            
            # Binarisation avec un seuil de 240
            _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
            
            # Configuration OCR selon le type de texte
            if is_rank or is_score:
                # Pour les rangs et scores, on utilise uniquement les chiffres
                result = self.reader.readtext(binary, allowlist='0123456789M', paragraph=False, detail=0)
            else:
                # Pour les noms et guildes, on utilise tous les caractères
                result = self.reader.readtext(binary, paragraph=False, detail=0)
            
            # Sauvegarder les images de debug
            debug_dir = os.path.join('data', 'debug', 'regions')
            os.makedirs(debug_dir, exist_ok=True)
            
            region_type = 'rank' if is_rank else 'score' if is_score else 'text'
            cv2.imwrite(os.path.join(debug_dir, f'original_{region_type}.png'), roi)
            cv2.imwrite(os.path.join(debug_dir, f'binary_{region_type}.png'), binary)
            
            # Retourner le premier résultat trouvé ou une chaîne vide
            return result[0] if result else ''
            
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction de texte : {str(e)}")
            return ''

    def _draw_extraction_zones(self, image):
        """
        Dessine les zones d'extraction sur l'image pour visualisation.
        
        Args:
            image: Image source
        
        Returns:
            Image avec les zones marquées
        """
        debug_image = image.copy()
        height, width = debug_image.shape[:2]
        
        # Couleurs pour les différentes zones
        colors = {
            'date': (0, 255, 0),    # Vert
            'rank': (255, 0, 0),    # Rouge
            'name': (0, 0, 255),    # Bleu
            'guild': (255, 255, 0),  # Jaune
            'score': (255, 0, 255)   # Magenta
        }
        
        # Zone de date
        date_x = int(width * 0.8)
        date_y = int(height * 0.1)
        cv2.rectangle(debug_image, (date_x, date_y), 
                     (date_x + 100, date_y + 30), colors['date'], 2)
        cv2.putText(debug_image, "Date", (date_x, date_y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['date'], 2)
        
        # Zones des entrées
        entry_height = 50
        start_y = int(height * 0.2)
        
        for i in range(5):
            base_y = start_y + (i * entry_height)
            
            # Rang
            rank_x = int(width * 0.05)
            cv2.rectangle(debug_image, 
                (rank_x, base_y),
                (rank_x + int(width * 0.1), base_y + entry_height),
                colors['rank'], 2)
            if i == 0:
                cv2.putText(debug_image, "Rang", (rank_x, start_y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['rank'], 2)
            
            # Nom
            name_x = int(width * 0.15)
            cv2.rectangle(debug_image,
                (name_x, base_y),
                (name_x + int(width * 0.3), base_y + entry_height),
                colors['name'], 2)
            if i == 0:
                cv2.putText(debug_image, "Nom", (name_x, start_y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['name'], 2)
            
            # Guilde
            guild_x = int(width * 0.45)
            cv2.rectangle(debug_image,
                (guild_x, base_y),
                (guild_x + int(width * 0.3), base_y + entry_height),
                colors['guild'], 2)
            if i == 0:
                cv2.putText(debug_image, "Guilde", (guild_x, start_y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['guild'], 2)
            
            # Score
            score_x = int(width * 0.75)
            cv2.rectangle(debug_image,
                (score_x, base_y),
                (score_x + int(width * 0.15), base_y + entry_height),
                colors['score'], 2)
            if i == 0:
                cv2.putText(debug_image, "Score", (score_x, start_y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['score'], 2)
        
        # Sauvegarder l'image de debug
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'debug')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'extraction_zones_{time.strftime("%Y%m%d_%H%M%S")}.png')
        cv2.imwrite(output_path, debug_image)
        logger.info(f"Image de debug sauvegardée : {output_path}")
        
        return debug_image

    def extract_data(self):
        """
        Extrait les données du classement en utilisant OCR par zones.
        
        Returns:
            list: Liste de dictionnaires contenant les données de chaque joueur
                 [{'rank': int, 'name': str, 'guild': str, 'score': str}, ...]
        """
        try:
            if not hasattr(self, 'captures') or not self.captures:
                logger.error("Aucune capture à analyser")
                return None
            
            # Charger la configuration des zones
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'config', 'ocr_zones.json')
            if not os.path.exists(config_path):
                logger.error("Configuration des zones OCR non trouvée")
                return None
            
            with open(config_path, 'r') as f:
                zones_config = json.load(f)
            
            # Dictionnaire pour stocker tous les joueurs (clé = rank pour éviter les doublons)
            all_players = {}
            
            # La date du classement est celle d'aujourd'hui
            current_date = datetime.now().strftime("%Y-%m-%d")
            date_j1 = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # J-1 est hier
            logger.info(f"Date du classement : {current_date} (J-1 : {date_j1})")
            
            # Vérifier si la date existe déjà dans ranking_dates
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT id FROM ranking_dates 
                WHERE date = ? AND type = ?
            """, (current_date, 'dreamland'))
            existing_date = cursor.fetchone()
            
            if not existing_date:
                logger.info(f"Création d'une nouvelle entrée pour la date {current_date}")
            else:
                logger.info(f"Mise à jour du classement pour la date {current_date}")
            
            # Traiter chaque capture
            for idx, image in enumerate(self.captures):
                self.current_image = image
                height, width = image.shape[:2]
                
                # Extraire les données des joueurs
                num_entries = len(zones_config['rank'])
                logger.debug(f"Traitement de la capture {idx+1}, recherche de {num_entries} entrées")
                
                for i in range(num_entries):
                    try:
                        # Extraire le rang
                        rank_zone = zones_config['rank'][i]
                        rank_x = int(rank_zone['x_percent'] * width)
                        rank_y = int(rank_zone['y_percent'] * height)
                        rank_w = int(rank_zone['width_percent'] * width)
                        rank_h = int(rank_zone['height_percent'] * height)
                        rank_text = self._extract_region(image, (rank_x, rank_y, rank_w, rank_h), is_rank=True)
                        
                        if not rank_text:
                            continue
                            
                        # Extraire le nom
                        name_zone = zones_config['name'][i]
                        name_x = int(name_zone['x_percent'] * width)
                        name_y = int(name_zone['y_percent'] * height)
                        name_w = int(name_zone['width_percent'] * width)
                        name_h = int(name_zone['height_percent'] * height)
                        name_text = self._extract_region(image, (name_x, name_y, name_w, name_h))
                        
                        # Extraire la guilde
                        guild_zone = zones_config['guild'][i]
                        guild_x = int(guild_zone['x_percent'] * width)
                        guild_y = int(guild_zone['y_percent'] * height)
                        guild_w = int(guild_zone['width_percent'] * width)
                        guild_h = int(guild_zone['height_percent'] * height)
                        guild_text = self._extract_region(image, (guild_x, guild_y, guild_w, guild_h))
                        
                        # Extraire le score
                        score_zone = zones_config['score'][i]
                        score_x = int(score_zone['x_percent'] * width)
                        score_y = int(score_zone['y_percent'] * height)
                        score_w = int(score_zone['width_percent'] * width)
                        score_h = int(score_zone['height_percent'] * height)
                        score_text = self._extract_region(image, (score_x, score_y, score_w, score_h), is_score=True)
                        
                        # Vérifier si l'entrée est valide
                        if rank_text and name_text:
                            try:
                                rank_digits = ''.join(filter(str.isdigit, rank_text))
                                if not rank_digits:
                                    continue
                                    
                                rank = int(rank_digits)
                                player = {
                                    'rank': rank,
                                    'name': name_text.strip(),
                                    'guild': guild_text.strip(),
                                    'score': ''.join(filter(str.isdigit, score_text)) or "0"
                                }
                                
                                # Ajouter ou mettre à jour le joueur
                                if rank not in all_players:
                                    all_players[rank] = player
                                    logger.debug(f"Nouveau joueur extrait : {player}")
                                else:
                                    logger.debug(f"Joueur déjà extrait au rang {rank}, ignoré")
                                
                            except ValueError as ve:
                                logger.warning(f"Impossible de convertir le rang '{rank_text}' : {ve}")
                                continue
                    
                    except Exception as e:
                        logger.warning(f"Erreur lors de l'extraction de l'entrée {i+1} de la capture {idx+1}: {e}")
                        continue
            
            # Convertir le dictionnaire en liste triée par rang
            players = [all_players[rank] for rank in sorted(all_players.keys())]
            logger.info(f"Nombre total de joueurs extraits : {len(players)}")
            
            # Sauvegarder les données dans la base de données
            if players:
                try:
                    self.db.save_ranking('dreamland', players, current_date, date_j1)
                    return players
                except Exception as e:
                    logger.error(f"Erreur lors de l'extraction des données : {e}")
                    return None
            
            return None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données : {e}")
            return None 