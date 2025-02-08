"""
Interface graphique pour le mapping des positions des boutons.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from PIL import Image, ImageTk
import cv2
import numpy as np
from loguru import logger

from .capture import capture_window, find_game_windows
from .config_writer import save_mapping, load_mapping

class MappingGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rank Tracker - Configuration des positions")
        
        # Obtenir la résolution de l'écran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculer les dimensions de la fenêtre (80% de l'écran)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Centrer la fenêtre
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Variables
        self.current_ranking = tk.StringVar(value="dreamland")
        self.current_image = None
        self.current_positions = {}
        self.screenshot = None
        self.selected_window = tk.StringVar()
        self.window_list = []
        self.current_hwnd = None
        self.last_click_x = 0
        self.last_click_y = 0
        
        self._setup_ui()
        self._load_existing_config()
        self._refresh_window_list()
    
    def _setup_ui(self):
        """Configuration de l'interface utilisateur."""
        # Frame principale avec scrollbar
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurer le redimensionnement
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Canvas et scrollbar pour le contenu principal
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # Frame principale
        main_frame = ttk.Frame(canvas, padding="10")
        
        # Configurer le scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Placer les widgets
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Créer une fenêtre dans le canvas pour la frame principale
        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Configurer le redimensionnement du container
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Sélection du type de classement
        ranking_frame = ttk.LabelFrame(main_frame, text="Type de classement", padding="5")
        ranking_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        rankings = [
            ("Royaume Onirique", "dreamland"),
            ("Arène", "arena"),
            ("Arène Suprême", "supreme_arena"),
            ("Suprématie de Guilde", "guild")
        ]
        
        for i, (text, value) in enumerate(rankings):
            ttk.Radiobutton(ranking_frame, text=text, value=value,
                          variable=self.current_ranking,
                          command=self._on_ranking_change).grid(row=0, column=i, padx=5)
        
        # Sélection de la fenêtre
        window_frame = ttk.LabelFrame(main_frame, text="Sélection de la fenêtre", padding="5")
        window_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.window_combo = ttk.Combobox(window_frame, textvariable=self.selected_window, state="readonly")
        self.window_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(window_frame, text="Rafraîchir", command=self._refresh_window_list).grid(row=0, column=1, padx=5)
        
        # Boutons d'action (placés avant la zone de capture pour être toujours visibles)
        button_frame = ttk.Frame(main_frame, padding="5")
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame, text="Capturer", command=self._capture_screen).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Sauvegarder", command=self._save_position).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Réinitialiser", command=self._reset_positions).grid(row=0, column=2, padx=5)
        
        # Zone de capture avec scrollbars
        capture_frame = ttk.LabelFrame(main_frame, text="Capture d'écran", padding="5")
        capture_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Canvas pour la capture avec scrollbars
        canvas_container = ttk.Frame(capture_frame)
        canvas_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(canvas_container, width=750, height=1334)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Placement des widgets de capture
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Liste des positions
        positions_frame = ttk.LabelFrame(main_frame, text="Positions configurées", padding="5")
        positions_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.positions_list = ttk.Treeview(positions_frame, columns=("x", "y"), show="headings", height=5)
        self.positions_list.heading("x", text="X")
        self.positions_list.heading("y", text="Y")
        self.positions_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(positions_frame, orient=tk.VERTICAL, command=self.positions_list.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.positions_list.configure(yscrollcommand=scrollbar.set)
        
        # Mettre à jour les scrollbars
        main_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Configurer le scrolling avec la molette de la souris
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _load_existing_config(self):
        """Charge la configuration existante si elle existe."""
        self.current_positions = load_mapping(self.current_ranking.get())
        self._update_positions_list()
        logger.info(f"Configuration chargée pour {self.current_ranking.get()}")
    
    def _refresh_window_list(self):
        """Rafraîchit la liste des fenêtres de jeu disponibles."""
        self.window_list = find_game_windows()
        window_titles = [w[1] for w in self.window_list]
        
        if not window_titles:
            logger.warning("Aucune fenêtre de jeu trouvée")
            window_titles = ["Aucune fenêtre de jeu trouvée"]
        
        self.window_combo['values'] = window_titles
        self.window_combo.set(window_titles[0])
        
        # Afficher un message si aucune fenêtre de jeu n'est trouvée
        if len(self.window_list) == 0:
            messagebox.showwarning(
                "Attention",
                "Aucune fenêtre de jeu n'a été trouvée.\n"
                "Assurez-vous que le jeu est lancé et visible à l'écran."
            )
    
    def _get_selected_hwnd(self):
        """Récupère le handle de la fenêtre sélectionnée."""
        if not self.window_list:
            return None
            
        selected_title = self.selected_window.get()
        for hwnd, title in self.window_list:
            if title == selected_title:
                return hwnd
        return None
    
    def _capture_screen(self):
        """Capture l'écran du jeu."""
        try:
            hwnd = self._get_selected_hwnd()
            if hwnd is None:
                messagebox.showerror(
                    "Erreur",
                    "Impossible de capturer l'écran.\n"
                    "Assurez-vous qu'une fenêtre de jeu est sélectionnée."
                )
                return
            
            self.current_hwnd = hwnd
            self.screenshot = capture_window(hwnd)
            
            if self.screenshot is not None:
                # Convertir pour affichage
                self.current_image = self.screenshot  # Garder l'image originale en BGR
                image = Image.fromarray(cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2RGB))
                self.photo_image = ImageTk.PhotoImage(image)  # Pour l'affichage
                
                # Effacer le canvas et afficher la nouvelle image
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
                
                # Configurer la région de défilement
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                logger.info("Capture d'écran réussie")
            else:
                messagebox.showerror(
                    "Erreur",
                    "La capture a échoué.\n"
                    "Essayez de relancer le jeu ou de le mettre en plein écran."
                )
        except Exception as e:
            logger.error(f"Erreur lors de la capture : {e}")
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de la capture :\n{str(e)}"
            )
    
    def _on_canvas_click(self, event):
        """Gère le clic sur le canvas."""
        if self.current_image is None:
            return
            
        # Calculer les coordonnées relatives à l'image
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_height, image_width = self.current_image.shape[:2]  # OpenCV image
        
        # Calculer les offsets pour centrer l'image
        x_offset = (canvas_width - image_width) // 2
        y_offset = (canvas_height - image_height) // 2
        
        # Ajuster les coordonnées en fonction des offsets
        x = event.x - x_offset
        y = event.y - y_offset
        
        # Vérifier que le clic est dans l'image
        if 0 <= x < image_width and 0 <= y < image_height:
            self.last_click_x = x
            self.last_click_y = y
            logger.info(f"Clic sur l'image : x={x}, y={y}")
            
            # Dessiner un point rouge à l'endroit du clic
            self._draw_click_point(event.x, event.y)
    
    def _update_positions_list(self):
        """Met à jour la liste des positions."""
        # Effacer la liste actuelle
        for item in self.positions_list.get_children():
            self.positions_list.delete(item)
        
        # Ajouter les positions
        for name, pos in self.current_positions.items():
            if isinstance(pos, dict) and "x" in pos and "y" in pos:
                self.positions_list.insert("", tk.END, text=name, values=(pos["x"], pos["y"]))
            else:
                logger.warning(f"Position invalide ignorée : {name} = {pos}")
    
    def _save_position(self):
        """Sauvegarde la position actuelle."""
        if self.current_image is None:
            messagebox.showwarning("Attention", "Veuillez d'abord capturer une image.")
            return
        
        # Demander le nom de la position
        name = simpledialog.askstring("Nom de la position", "Entrez un nom pour cette position :")
        if not name:
            return
        
        # Sauvegarder la position
        self.current_positions[name] = {
            "x": self.last_click_x,
            "y": self.last_click_y
        }
        
        # Mettre à jour l'affichage
        self._update_positions_list()
        
        # Sauvegarder dans le fichier
        save_mapping(self.current_ranking.get(), self.current_positions)
        
        logger.info(f"Position '{name}' sauvegardée : x={self.last_click_x}, y={self.last_click_y}")
    
    def _reset_positions(self):
        """Réinitialise les positions."""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment réinitialiser toutes les positions ?"):
            self.current_positions = {}
            self._update_positions_list()
            if self.screenshot is not None:
                self._capture_screen()  # Rafraîchit l'affichage
    
    def _on_ranking_change(self):
        """Gère le changement de type de classement."""
        self._load_existing_config()
        if self.screenshot is not None:
            self._capture_screen()  # Rafraîchit l'affichage
    
    def _draw_click_point(self, x, y):
        """Dessine un point rouge à l'endroit du clic."""
        # Effacer les points précédents
        self.canvas.delete("click_point")
        
        # Dessiner un nouveau point
        point_size = 5
        self.canvas.create_oval(
            x - point_size, y - point_size,
            x + point_size, y + point_size,
            fill="red",
            tags="click_point"
        )
        
        # Ajouter les coordonnées
        self.canvas.create_text(
            x, y - 15,
            text=f"({self.last_click_x}, {self.last_click_y})",
            fill="red",
            tags="click_point"
        )
    
    def run(self):
        """Lance l'application."""
        self.root.mainloop()

def main():
    """Point d'entrée de l'application."""
    logger.info("Démarrage de l'application de mapping")
    app = MappingGUI()
    app.run()

if __name__ == "__main__":
    main() 