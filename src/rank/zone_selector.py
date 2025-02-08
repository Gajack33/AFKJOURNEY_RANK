"""
Outil de sélection des zones pour l'OCR.
"""

import cv2
import numpy as np
import json
import os
from loguru import logger

class ZoneSelector:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        self.original = self.image.copy()
        self.zones = {}
        self.current_zone = None
        self.drawing = False
        self.start_point = None
        self.window_name = "Zone Selector"
        
        # Liste des zones à définir
        self.zones_to_define = [
            ("date_j1", "Sélectionnez la zone J-1"),
            ("date_j2", "Sélectionnez la zone J-2"),
            ("rank", "Sélectionnez les zones de rang (Espace pour terminer)"),
            ("name", "Sélectionnez les zones de nom (Espace pour terminer)"),
            ("guild", "Sélectionnez les zones de guilde (Espace pour terminer)"),
            ("score", "Sélectionnez les zones de score (Espace pour terminer)")
        ]
        self.current_zone_index = 0
        
        # Couleurs pour les zones
        self.colors = {
            'date_j1': (0, 255, 0),    # Vert
            'date_j2': (0, 200, 0),    # Vert foncé
            'rank': (255, 0, 0),    # Rouge
            'name': (0, 0, 255),    # Bleu
            'guild': (255, 255, 0),  # Jaune
            'score': (255, 0, 255)   # Magenta
        }
        
        # Initialiser les listes pour chaque type de zone
        for zone_name, _ in self.zones_to_define:
            self.zones[zone_name] = []
    
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.image = self.original.copy()
            self._draw_existing_zones()
            
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            img_copy = self.image.copy()
            cv2.rectangle(img_copy, self.start_point, (x, y), 
                         self.colors[self.zones_to_define[self.current_zone_index][0]], 2)
            cv2.imshow(self.window_name, img_copy)
            
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if self.start_point:
                zone_name = self.zones_to_define[self.current_zone_index][0]
                zone = {
                    'x': min(self.start_point[0], x),
                    'y': min(self.start_point[1], y),
                    'width': abs(x - self.start_point[0]),
                    'height': abs(y - self.start_point[1])
                }
                self.zones[zone_name].append(zone)
                
                # Dessiner le rectangle et ajouter un numéro
                cv2.rectangle(self.image, self.start_point, (x, y),
                            self.colors[zone_name], 2)
                cv2.putText(self.image, f"{zone_name}_{len(self.zones[zone_name])}", 
                           (self.start_point[0], self.start_point[1] - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors[zone_name], 2)
                
                # Passer à la zone suivante pour les dates
                if zone_name.startswith('date_'):
                    self.current_zone_index += 1
                    print(f"\n{self.zones_to_define[self.current_zone_index][1]}")
    
    def _draw_existing_zones(self):
        for zone_name, zones_list in self.zones.items():
            for i, coords in enumerate(zones_list, 1):
                cv2.rectangle(self.image,
                            (coords['x'], coords['y']),
                            (coords['x'] + coords['width'], coords['y'] + coords['height']),
                            self.colors[zone_name], 2)
                cv2.putText(self.image, f"{zone_name}_{i}", 
                           (coords['x'], coords['y'] - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors[zone_name], 2)
    
    def run(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print(f"\n{self.zones_to_define[0][1]}")
        
        while True:
            cv2.imshow(self.window_name, self.image)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):  # Sauvegarder
                if self.current_zone_index >= len(self.zones_to_define):
                    self.save_zones()
                    break
                else:
                    print("\nVeuillez définir toutes les zones avant de sauvegarder.")
            
            elif key == ord('r'):  # Recommencer
                self.zones = {name: [] for name, _ in self.zones_to_define}
                self.current_zone_index = 0
                self.image = self.original.copy()
                print(f"\n{self.zones_to_define[0][1]}")
            
            elif key == 32:  # Espace pour passer à la zone suivante
                if self.current_zone_index > 0:  # Pas pour la date
                    zone_name = self.zones_to_define[self.current_zone_index][0]
                    if len(self.zones[zone_name]) > 0:  # Au moins une zone définie
                        self.current_zone_index += 1
                        if self.current_zone_index < len(self.zones_to_define):
                            print(f"\n{self.zones_to_define[self.current_zone_index][1]}")
                        else:
                            print("\nToutes les zones ont été définies. Appuyez sur 'S' pour sauvegarder ou 'R' pour recommencer.")
            
            elif key == 27:  # Échap pour quitter
                break
        
        cv2.destroyAllWindows()
    
    def save_zones(self):
        # Calculer les pourcentages relatifs
        height, width = self.image.shape[:2]
        zones_percent = {}
        
        for zone_name, zones_list in self.zones.items():
            zones_percent[zone_name] = []
            for coords in zones_list:
                zone_percent = {
                    'x_percent': coords['x'] / width,
                    'y_percent': coords['y'] / height,
                    'width_percent': coords['width'] / width,
                    'height_percent': coords['height'] / height
                }
                zones_percent[zone_name].append(zone_percent)
        
        # Sauvegarder dans un fichier JSON
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'config')
        config_path = os.path.join(config_dir, 'ocr_zones.json')
        
        # Créer le dossier si nécessaire
        os.makedirs(config_dir, exist_ok=True)
        
        # Sauvegarder la configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(zones_percent, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Zones sauvegardées dans {config_path}")

def main():
    """Point d'entrée pour la sélection des zones."""
    # Trouver la dernière capture
    captures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'captures')
    captures = [f for f in os.listdir(captures_dir) if f.startswith('dreamland_capture_')]
    
    if not captures:
        print("Aucune capture trouvée.")
        return
    
    latest_capture = sorted(captures)[-1]
    image_path = os.path.join(captures_dir, latest_capture)
    
    selector = ZoneSelector(image_path)
    selector.run()

if __name__ == "__main__":
    main() 