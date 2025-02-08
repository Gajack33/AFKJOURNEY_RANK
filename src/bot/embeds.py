"""
Générateur d'embeds Discord pour l'affichage des classements.
"""

import discord
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import DateFormatter
import io
from bot.config import BotConfig

class EmbedGenerator:
    """Classe pour générer les embeds Discord."""
    
    def __init__(self):
        self.config = BotConfig()
        
    def create_ranking_embed(self, title: str, players: list, date: datetime) -> discord.Embed:
        """Crée un embed pour afficher un classement.
        
        Args:
            title: Titre du classement
            players: Liste des joueurs et leurs scores
            date: Date du classement
        """
        embed = discord.Embed(
            title=title,
            color=self.config.colors["info"],
            timestamp=date
        )
        
        # Création du tableau formaté
        table = "```\n"
        # En-tête avec alignement
        table += "Rang    Joueur          Guilde        J-1    Moy30j\n"
        table += "─" * 50 + "\n"
        
        # Données des joueurs
        for player in players:
            # Formatage du rang (4 caractères + 2 espaces)
            rank = str(player['rank']).rjust(4) + "  "
            
            # Formatage du nom (15 caractères)
            name = player['name'][:15].ljust(15)
            
            # Formatage de la guilde (12 caractères)
            guild = (player['guild'] or 'Sans')[:12].ljust(12)
            
            # Formatage du changement de rang (6 caractères)
            if player['rank_change'] > 0:
                rank_change = f"(+{player['rank_change']})".rjust(6)
            elif player['rank_change'] < 0:
                rank_change = f"({player['rank_change']})".rjust(6)
            else:
                rank_change = "(=)".rjust(6)
            
            # Formatage de la moyenne (6 caractères)
            avg_rank = str(int(float(player['avg_rank']))).rjust(6)
            
            # Ajout de la ligne au tableau
            table += f"{rank}{name}{guild}{rank_change}  {avg_rank}\n"
            
        table += "```"
        
        # Ajout du tableau à l'embed
        embed.description = table
        
        # Configuration du footer
        embed.set_footer(text=self.config.embed_config["footer_text"])
        
        if self.config.embed_config["thumbnail_url"]:
            embed.set_thumbnail(url=self.config.embed_config["thumbnail_url"])
            
        return embed
        
    def create_player_embed(self, player_name: str, history: list) -> discord.Embed:
        """Crée un embed pour afficher l'historique d'un joueur.
        
        Args:
            player_name: Nom du joueur
            history: Historique des classements du joueur
        """
        embed = discord.Embed(
            title=f"Historique de {player_name}",
            color=self.config.colors["info"]
        )
        
        # TODO: Ajouter la génération du graphique de progression
        # TODO: Ajouter les statistiques du joueur
        
        embed.set_footer(text=self.config.embed_config["footer_text"])
        
        return embed
        
    def create_error_embed(self, message: str) -> discord.Embed:
        """Crée un embed pour afficher une erreur.
        
        Args:
            message: Message d'erreur à afficher
        """
        embed = discord.Embed(
            title="Erreur",
            description=message,
            color=self.config.colors["error"]
        )
        
        embed.set_footer(text=self.config.embed_config["footer_text"])
        
        return embed
        
    def create_player_history_embed(self, player_name: str, history: list) -> discord.Embed:
        """Crée un embed pour afficher l'historique d'un joueur.
        
        Args:
            player_name: Nom du joueur
            history: Liste des classements avec date, rang et score
        """
        embed = discord.Embed(
            title=f"Historique de {player_name} - Royaume Onirique",
            color=self.config.colors["info"]
        )
        
        # Création du tableau formaté
        table = "```\n"
        # En-tête avec alignement
        table += "Date         Rang    J-1    Moy30j\n"
        table += "─" * 40 + "\n"
        
        # Données des classements
        for i in range(len(history)):
            # Formatage de la date (JJ/MM/YY)
            date = datetime.strptime(history[i]['date'], "%Y-%m-%d").strftime("%d/%m/%y")
            
            # Formatage du rang (4 caractères + 2 espaces)
            rank = str(history[i]['rank']).rjust(4) + "  "
            
            # Calcul et formatage du changement de rang par rapport au jour précédent
            if i < len(history) - 1:  # S'il y a un jour suivant
                rank_change = history[i+1]['rank'] - history[i]['rank']  # Jour précédent - Jour actuel
                if rank_change > 0:
                    rank_change_str = f"(+{rank_change})".rjust(6)
                elif rank_change < 0:
                    rank_change_str = f"({rank_change})".rjust(6)
                else:
                    rank_change_str = "(=)".rjust(6)
            else:
                rank_change_str = "".rjust(6)
            
            # Formatage de la moyenne sur 30 jours
            avg_rank = str(int(float(history[i]['avg_rank']))).rjust(6)
            
            # Ajout de la ligne au tableau
            table += f"{date}    {rank}{rank_change_str}  {avg_rank}\n"
        
        table += "```"
        
        # Ajout du tableau à l'embed
        embed.description = table
        
        # Configuration du footer
        embed.set_footer(text=self.config.embed_config["footer_text"])
        
        if self.config.embed_config["thumbnail_url"]:
            embed.set_thumbnail(url=self.config.embed_config["thumbnail_url"])
            
        return embed

    def create_progression_embed(self, player_name: str, history: list) -> discord.Embed:
        """Crée un embed avec un graphique de progression pour un joueur.
        
        Args:
            player_name: Nom du joueur
            history: Liste des classements avec date et rang
        """
        # Création du graphique
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        
        # Préparation des données
        dates = []
        ranks = []
        for entry in reversed(history):  # On inverse pour avoir l'ordre chronologique
            date = datetime.strptime(entry['date'], "%Y-%m-%d")
            dates.append(date)
            ranks.append(entry['rank'])
        
        # Création du graphique
        plt.plot(dates, ranks, 'b-', marker='o')
        
        # Configuration des axes
        plt.gca().invert_yaxis()  # Inverser l'axe Y car rang 1 est meilleur
        plt.ylim(100.5, 0.5)  # Limiter l'axe Y de 1 à 100
        plt.gca().yaxis.set_major_locator(MultipleLocator(10))  # Graduations tous les 10 rangs
        
        # Personnalisation
        plt.title(f"Progression de {player_name} - Royaume Onirique", color='white', pad=20)
        plt.xlabel("Date", color='white')
        plt.ylabel("Rang", color='white')
        plt.grid(True, linestyle='--', alpha=0.3)
        
        # Format des dates en bas du graphique
        date_formatter = DateFormatter('%d/%m')
        plt.gca().xaxis.set_major_formatter(date_formatter)
        plt.xticks(rotation=45)
        
        # Ajustement du layout
        plt.tight_layout()
        
        # Conversion du graphique en bytes pour Discord
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor='#2f3136')
        buffer.seek(0)
        plt.close()
        
        # Création de l'embed
        embed = discord.Embed(
            title=f"Progression de {player_name}",
            color=self.config.colors["info"]
        )
        
        # Ajout des statistiques
        if len(ranks) > 1:
            rank_change = ranks[0] - ranks[-1]
            if rank_change > 0:
                trend = f"↗️ Gain de {rank_change} places"
            elif rank_change < 0:
                trend = f"↘️ Perte de {abs(rank_change)} places"
            else:
                trend = "➡️ Position stable"
            
            # Ajout du meilleur et du pire rang
            best_rank = min(ranks)
            worst_rank = max(ranks)
            stats = f"{trend}\n"
            stats += f"Meilleur rang : {best_rank}\n"
            stats += f"Pire rang : {worst_rank}"
            
            embed.add_field(name="Statistiques", value=stats, inline=False)
        
        # Ajout du graphique comme image
        file = discord.File(buffer, filename="progression.png")
        embed.set_image(url="attachment://progression.png")
        
        return embed, file 