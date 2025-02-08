import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from loguru import logger
import win32gui
import win32api
import win32con
import win32process
import ctypes
import cv2

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mapper.capture import find_game_windows

# Constantes pour mouse_event
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001

def is_admin():
    """Vérifie si le script est exécuté en tant qu'administrateur."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class InteractionTester(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Test d'interaction avec le jeu")
        self.geometry("400x600")
        
        self.hwnd = None
        self.setup_ui()
        self.refresh_window_list()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Frame principale
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sélection de la fenêtre
        window_frame = ttk.LabelFrame(main_frame, text="Sélection de la fenêtre", padding="5")
        window_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.window_combo = ttk.Combobox(window_frame, state="readonly")
        self.window_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(window_frame, text="Rafraîchir", command=self.refresh_window_list).grid(row=0, column=1, padx=5)
        
        # Tests de base
        basic_frame = ttk.LabelFrame(main_frame, text="Tests de base", padding="5")
        basic_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(basic_frame, text="Activer la fenêtre", command=self.test_activate).grid(row=0, column=0, pady=5, padx=5)
        ttk.Button(basic_frame, text="Tester un clic (centre)", command=self.test_click).grid(row=1, column=0, pady=5, padx=5)
        ttk.Button(basic_frame, text="Position curseur", command=self.show_cursor_pos).grid(row=2, column=0, pady=5, padx=5)
        ttk.Button(basic_frame, text="Déplacer souris", command=self.test_mouse_move).grid(row=3, column=0, pady=5, padx=5)
        
        # Tests de coordonnées
        coord_frame = ttk.LabelFrame(main_frame, text="Test de coordonnées", padding="5")
        coord_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, padx=5)
        self.x_entry = ttk.Entry(coord_frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5)
        self.x_entry.insert(0, "375")
        
        ttk.Label(coord_frame, text="Y:").grid(row=0, column=2, padx=5)
        self.y_entry = ttk.Entry(coord_frame, width=10)
        self.y_entry.grid(row=0, column=3, padx=5)
        self.y_entry.insert(0, "500")
        
        ttk.Button(coord_frame, text="Tester le clic", command=self.test_coord_click).grid(row=1, column=0, columnspan=4, pady=5)
        
        # Méthode de clic
        click_frame = ttk.LabelFrame(main_frame, text="Méthode de clic", padding="5")
        click_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.click_method = tk.StringVar(value="mouse_event")
        ttk.Radiobutton(click_frame, text="mouse_event", value="mouse_event", variable=self.click_method).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(click_frame, text="SendMessage", value="sendmessage", variable=self.click_method).grid(row=0, column=1, padx=5)
        ttk.Radiobutton(click_frame, text="PyAutoGUI", value="pyautogui", variable=self.click_method).grid(row=0, column=2, padx=5)
        
        # Logs
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
        log_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=40)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def log(self, message):
        """Ajoute un message aux logs."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        logger.info(message)
    
    def refresh_window_list(self):
        """Rafraîchit la liste des fenêtres."""
        self.windows = find_game_windows()
        window_titles = [w[1] for w in self.windows]
        
        if not window_titles:
            window_titles = ["Aucune fenêtre trouvée"]
        
        self.window_combo['values'] = window_titles
        self.window_combo.set(window_titles[0])
        
        if self.windows:
            self.hwnd = self.windows[0][0]
            self.log(f"Fenêtre sélectionnée : {window_titles[0]}")
    
    def move_mouse_to(self, target_x, target_y):
        """
        Déplace la souris progressivement vers une position cible.
        
        Args:
            target_x (int): Coordonnée X cible
            target_y (int): Coordonnée Y cible
        """
        current_pos = win32gui.GetCursorPos()
        self.log(f"Déplacement souris de {current_pos} vers ({target_x}, {target_y})")
        
        steps = 20
        for i in range(steps + 1):
            x = current_pos[0] + ((target_x - current_pos[0]) * i // steps)
            y = current_pos[1] + ((target_y - current_pos[1]) * i // steps)
            ctypes.windll.user32.SetCursorPos(x, y)
            time.sleep(0.02)
        
        final_pos = win32gui.GetCursorPos()
        self.log(f"Position finale de la souris : {final_pos}")

    def send_click(self, x, y, method="mouse_event"):
        """
        Envoie un clic aux coordonnées spécifiées.
        
        Args:
            x (int): Coordonnée X écran absolue
            y (int): Coordonnée Y écran absolue
            method (str): Méthode de clic (mouse_event, sendmessage, pyautogui)
        """
        # Activer la fenêtre avant le clic
        self.test_activate()
        time.sleep(0.5)  # Délai augmenté
        
        try:
            # Déplacer la souris vers la position cible
            self.move_mouse_to(x, y)
            time.sleep(0.2)
            
            # Clic selon la méthode choisie
            if method == "mouse_event":
                win32api.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.1)
                win32api.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                self.log(f"Clic mouse_event effectué à la position actuelle")
                
            elif method == "sendmessage":
                client_pos = win32gui.ScreenToClient(self.hwnd, (int(x), int(y)))
                lparam = win32api.MAKELONG(client_pos[0], client_pos[1])
                
                win32gui.PostMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
                time.sleep(0.1)
                win32gui.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
                time.sleep(0.1)
                win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
                time.sleep(0.1)
                win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lparam)
                self.log(f"Clic SendMessage effectué avec coordonnées client")
                
            else:  # pyautogui
                import pyautogui
                pyautogui.PAUSE = 0.1
                pyautogui.FAILSAFE = True
                pyautogui.click()
                self.log(f"Clic PyAutoGUI effectué")
                
        except Exception as e:
            self.log(f"Erreur lors du clic : {e}")
    
    def test_activate(self):
        """Teste l'activation de la fenêtre."""
        if not self.hwnd:
            self.log("Aucune fenêtre sélectionnée")
            return
        
        try:
            # Restaurer la fenêtre si minimisée
            if win32gui.IsIconic(self.hwnd):
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            
            # Gestion des threads pour forcer l'activation
            fore_thread = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
            current_thread = win32api.GetCurrentThreadId()
            
            if fore_thread[0] != current_thread:
                win32process.AttachThreadInput(current_thread, fore_thread[0], True)
            
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.SetActiveWindow(self.hwnd)
            win32gui.BringWindowToTop(self.hwnd)
            
            time.sleep(0.1)
            if fore_thread[0] != current_thread:
                win32process.AttachThreadInput(current_thread, fore_thread[0], False)
            
            self.log("Fenêtre activée avec succès")
        except Exception as e:
            self.log(f"Erreur lors de l'activation : {e}")
    
    def test_click(self):
        """Teste un clic au centre de la fenêtre."""
        if not self.hwnd:
            self.log("Aucune fenêtre sélectionnée")
            return
        
        try:
            # Obtenir les dimensions de la fenêtre
            rect = win32gui.GetWindowRect(self.hwnd)
            center_x = rect[0] + (rect[2] - rect[0]) // 2
            center_y = rect[1] + (rect[3] - rect[1]) // 2
            
            self.log(f"Dimensions fenêtre : {rect}")
            self.log(f"Clic au centre : ({center_x}, {center_y})")
            
            # Utiliser la méthode sélectionnée
            self.send_click(center_x, center_y, self.click_method.get())
            
        except Exception as e:
            self.log(f"Erreur : {e}")
    
    def test_coord_click(self):
        """Teste un clic aux coordonnées spécifiées."""
        if not self.hwnd:
            self.log("Aucune fenêtre sélectionnée")
            return
        
        try:
            # Obtenir les coordonnées relatives à la fenêtre
            rect = win32gui.GetWindowRect(self.hwnd)
            x = rect[0] + int(self.x_entry.get())
            y = rect[1] + int(self.y_entry.get())
            
            if not self.x_entry.get().isdigit() or not self.y_entry.get().isdigit():
                self.log("Coordonnées invalides")
                return
            
            self.log(f"Dimensions fenêtre : {rect}")
            self.log(f"Clic aux coordonnées : ({x}, {y})")
            
            # Cliquer aux coordonnées spécifiées
            self.send_click(x, y, self.click_method.get())
            
        except Exception as e:
            self.log(f"Erreur lors du clic : {e}")

    def show_cursor_pos(self):
        """Affiche la position actuelle du curseur."""
        try:
            # Obtenir la position du curseur
            cursor_pos = win32gui.GetCursorPos()
            
            # Si une fenêtre est sélectionnée, convertir en coordonnées client
            if self.hwnd:
                screen_pos = cursor_pos
                client_pos = win32gui.ScreenToClient(self.hwnd, cursor_pos)
                self.log(f"Position curseur - Écran: {screen_pos}, Client: {client_pos}")
            else:
                self.log(f"Position curseur: {cursor_pos}")
        except Exception as e:
            self.log(f"Erreur lors de la récupération de la position : {e}")

    def test_mouse_move(self):
        """Teste le déplacement de la souris vers l'application."""
        if not self.hwnd:
            self.log("Aucune fenêtre sélectionnée")
            return
            
        try:
            # Obtenir les dimensions de la fenêtre
            rect = win32gui.GetWindowRect(self.hwnd)
            
            # Calculer le centre de la fenêtre
            center_x = rect[0] + (rect[2] - rect[0]) // 2
            center_y = rect[1] + (rect[3] - rect[1]) // 2
            
            # Déplacer la souris vers le centre
            self.move_mouse_to(center_x, center_y)
            self.log("Déplacement terminé")
            
        except Exception as e:
            self.log(f"Erreur lors du déplacement : {e}")

    def _draw_extraction_zones(self, image):
        """
        Dessine les zones d'extraction sur l'image pour visualisation.
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
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'data', 'debug')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'extraction_zones_{time.strftime("%Y%m%d_%H%M%S")}.png')
        cv2.imwrite(output_path, debug_image)
        logger.info(f"Image de debug sauvegardée : {output_path}")
        
        return debug_image

def main():
    """Point d'entrée de l'application."""
    if not is_admin():
        messagebox.showerror(
            "Privilèges insuffisants",
            "Cette application nécessite des privilèges administrateur pour fonctionner correctement.\n"
            "Veuillez la relancer en tant qu'administrateur."
        )
        sys.exit(1)
    
    app = InteractionTester()
    app.mainloop()

if __name__ == "__main__":
    main()