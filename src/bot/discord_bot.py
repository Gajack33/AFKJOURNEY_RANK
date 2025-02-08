"""
Bot Discord pour l'affichage des classements AFK Journey.
"""

import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from loguru import logger
from .commands import RankingCommands
from .config import BotConfig

# Chargement des variables d'environnement
load_dotenv()

class RankingBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.config = BotConfig()
        self.commands = RankingCommands(self)
        
    async def setup_hook(self):
        """Configuration initiale du bot."""
        logger.info("Configuration du bot Discord...")
        self.commands.setup()
        await self.tree.sync()
        
    async def on_ready(self):
        """Événement appelé quand le bot est prêt."""
        logger.info(f"Bot connecté en tant que {self.user}")
        logger.info("Commandes disponibles :")
        logger.info("  /royaumeonirique - Affiche le classement du Royaume Onirique")
        logger.info("  /progression <joueur> - Affiche la progression d'un joueur")

async def main():
    """Point d'entrée principal du bot."""
    # Récupération du token depuis une variable d'environnement
    token = os.getenv("DISCORD_TOKEN")
    if not token or token == "votre_token_ici":
        logger.error("Token Discord non configuré dans le fichier .env")
        return
        
    client = RankingBot()
    await client.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 