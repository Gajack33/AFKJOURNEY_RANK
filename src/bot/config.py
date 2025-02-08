"""
Configuration du bot Discord.
"""

import os
from dataclasses import dataclass

@dataclass
class BotConfig:
    """Configuration du bot Discord."""
    token: str = os.getenv("DISCORD_TOKEN", "")
    command_prefix: str = "!"
    
    # Couleurs pour les embeds
    colors = {
        "success": 0x2ecc71,  # Vert
        "error": 0xe74c3c,    # Rouge
        "info": 0x3498db      # Bleu
    }
    
    # Configuration des embeds
    embed_config = {
        "footer_text": "AFK Journey Rankings",
        "thumbnail_url": "",  # URL de l'image à ajouter plus tard
    }
    
    # Messages d'erreur
    error_messages = {
        "db_error": "Une erreur est survenue lors de la récupération des données.",
        "player_not_found": "Joueur non trouvé dans la base de données.",
        "invalid_command": "Commande invalide. Utilisez /help pour voir la liste des commandes disponibles."
    } 