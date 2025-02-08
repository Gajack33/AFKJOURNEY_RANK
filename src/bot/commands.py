"""
Commandes du bot Discord pour l'affichage des classements.
"""

from discord import app_commands
import discord
from loguru import logger
from rank.database import RankDatabase
from bot.embeds import EmbedGenerator
from datetime import datetime, timedelta

class RankingCommands:
    def __init__(self, bot):
        self.bot = bot
        self.db = RankDatabase()
        self.embed_generator = EmbedGenerator()
        
    def setup(self):
        """Configure les commandes du bot."""
        
        @self.bot.tree.command(name="royaumeonirique", description="Affiche le classement du Royaume Onirique")
        @app_commands.describe(
            joueur="Nom du joueur à rechercher",
            guilde="Nom de la guilde à filtrer",
            date="Date du classement (format: JJ/MM/YY)",
            hier="Afficher le classement d'hier"
        )
        async def royaume_onirique(
            interaction: discord.Interaction,
            joueur: str = None,
            guilde: str = None,
            date: str = None,
            hier: bool = False
        ):
            """Commande pour afficher le classement du Royaume Onirique."""
            await interaction.response.defer()
            
            try:
                # Gestion de la date
                target_date = None
                if hier:
                    target_date = datetime.now() - timedelta(days=1)
                elif date:
                    try:
                        target_date = datetime.strptime(date, "%d/%m/%y")
                    except ValueError:
                        await interaction.followup.send(
                            embed=self.embed_generator.create_error_embed("Format de date invalide. Utilisez le format JJ/MM/YY.")
                        )
                        return
                
                # Si un joueur est spécifié, afficher son historique
                if joueur:
                    history = self.db.get_player_history(joueur, limit=30)  # Récupère les 30 derniers jours
                    if not history:
                        await interaction.followup.send(
                            embed=self.embed_generator.create_error_embed(f"Aucun historique trouvé pour le joueur {joueur}.")
                        )
                        return
                    
                    # Création de l'embed avec l'historique
                    embed = self.embed_generator.create_player_history_embed(
                        player_name=joueur,
                        history=history
                    )
                    await interaction.followup.send(embed=embed)
                    return

                # Récupération des données avec les filtres
                players = self.db.get_latest_ranking(
                    limit=100,
                    guild_name=guilde,
                    target_date=target_date
                )
                
                if not players:
                    error_message = "Aucun classement disponible"
                    if guilde:
                        error_message += f" pour la guilde {guilde}"
                    if target_date:
                        error_message += f" à la date du {target_date.strftime('%d/%m/%y')}"
                    await interaction.followup.send(
                        embed=self.embed_generator.create_error_embed(error_message + ".")
                    )
                    return
                
                # Division des joueurs en groupes de 25
                player_groups = [players[i:i + 25] for i in range(0, len(players), 25)]
                
                # Formatage de la date
                display_date = target_date.strftime("%d/%m/%Y") if target_date else datetime.now().strftime("%d/%m/%Y")
                
                # Construction du titre
                base_title = f"Classement du Royaume Onirique du {display_date}"
                if guilde:
                    base_title += f" - Guilde: {guilde}"
                
                # Envoi des embeds
                for i, group in enumerate(player_groups):
                    start_rank = i * 25 + 1
                    end_rank = start_rank + len(group) - 1
                    embed = self.embed_generator.create_ranking_embed(
                        title=f"{base_title} ({start_rank}-{end_rank})",
                        players=group,
                        date=target_date or datetime.now()
                    )
                    await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'affichage du classement: {e}")
                await interaction.followup.send(
                    embed=self.embed_generator.create_error_embed("Une erreur est survenue lors de la récupération du classement.")
                )
                
        @self.bot.tree.command(name="progression", description="Affiche la progression d'un joueur sur les 10 derniers jours")
        @app_commands.describe(
            joueur="Nom du joueur à rechercher"
        )
        async def progression(interaction: discord.Interaction, joueur: str):
            """Commande pour afficher la progression d'un joueur."""
            await interaction.response.defer()
            
            try:
                # Récupération de l'historique des 10 derniers jours
                history = self.db.get_player_history(joueur, limit=10)
                if not history:
                    await interaction.followup.send(
                        embed=self.embed_generator.create_error_embed(f"Aucun historique trouvé pour le joueur {joueur}.")
                    )
                    return
                    
                # Création du graphique et de l'embed
                embed, file = self.embed_generator.create_progression_embed(joueur, history)
                await interaction.followup.send(file=file, embed=embed)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'affichage de la progression: {e}")
                await interaction.followup.send(
                    embed=self.embed_generator.create_error_embed("Une erreur est survenue lors de la récupération des données.")
                ) 