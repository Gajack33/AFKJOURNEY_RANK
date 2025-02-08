"""
Module de gestion de la base de données pour le stockage des classements.
"""

import sqlite3
import os
from datetime import datetime
from loguru import logger
import time

class RankDatabase:
    """Gestionnaire de la base de données des classements."""
    
    def __init__(self):
        """Initialise la connexion à la base de données."""
        # Créer le dossier resources/data s'il n'existe pas
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'data', 'database')
        os.makedirs(data_dir, exist_ok=True)
        
        # Chemin de la base de données
        self.db_path = os.path.join(data_dir, 'rankings.db')
        
        # Initialiser la connexion
        self.conn = sqlite3.connect(self.db_path)
        
        # Initialiser la base de données
        self._init_database()
    
    def __del__(self):
        """Ferme la connexion à la base de données."""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def _init_database(self):
        """Initialise la structure de la base de données."""
        try:
            cursor = self.conn.cursor()
            
            # Table des dates de classement
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ranking_dates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    date_j1 TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, type)
                )
            """)
            
            # Table des joueurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    guild TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name)
                )
            """)
            
            # Table des classements
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rankings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ranking_date_id INTEGER,
                    player_id INTEGER,
                    rank INTEGER NOT NULL,
                    score TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ranking_date_id) REFERENCES ranking_dates (id),
                    FOREIGN KEY (player_id) REFERENCES players (id),
                    UNIQUE(ranking_date_id, rank)
                )
            """)
            
            self.conn.commit()
            logger.info("Base de données initialisée avec succès")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données : {e}")
            raise
    
    def save_ranking(self, ranking_type, players, date, date_j1):
        """
        Sauvegarde les données d'un classement.
        
        Args:
            ranking_type (str): Type de classement (dreamland, arena, etc.)
            players (list): Liste des joueurs avec leurs données
            date (str): Date du classement
            date_j1 (str): Date du classement J-1
        """
        try:
            cursor = self.conn.cursor()
            
            # Vérifier si la date existe déjà
            cursor.execute("""
                SELECT id FROM ranking_dates
                WHERE date = ? AND type = ?
            """, (date, ranking_type))
            result = cursor.fetchone()
            
            if result:
                # La date existe, mettre à jour date_j1
                ranking_date_id = result[0]
                cursor.execute("""
                    UPDATE ranking_dates
                    SET date_j1 = ?
                    WHERE id = ?
                """, (date_j1, ranking_date_id))
            else:
                # La date n'existe pas, l'insérer
                cursor.execute("""
                    INSERT INTO ranking_dates (date, type, date_j1)
                    VALUES (?, ?, ?)
                """, (date, ranking_type, date_j1))
                
                cursor.execute("""
                    SELECT id FROM ranking_dates
                    WHERE date = ? AND type = ?
                """, (date, ranking_type))
                result = cursor.fetchone()
                if not result:
                    raise Exception("Impossible de récupérer l'ID de la date de classement")
                ranking_date_id = result[0]
            
            # Supprimer les anciens classements pour cette date
            cursor.execute("""
                DELETE FROM rankings
                WHERE ranking_date_id = ?
            """, (ranking_date_id,))
            
            # Traiter chaque joueur
            for player in players:
                # Insérer ou récupérer le joueur
                cursor.execute("""
                    INSERT OR IGNORE INTO players (name, guild)
                    VALUES (?, ?)
                """, (player['name'], player.get('guild', '')))
                
                cursor.execute("""
                    SELECT id FROM players WHERE name = ?
                """, (player['name'],))
                result = cursor.fetchone()
                if not result:
                    raise Exception(f"Impossible de récupérer l'ID du joueur {player['name']}")
                player_id = result[0]
                
                # Mettre à jour la guilde si elle a changé
                cursor.execute("""
                    UPDATE players
                    SET guild = ?
                    WHERE id = ? AND guild != ?
                """, (player.get('guild', ''), player_id, player.get('guild', '')))
                
                # Insérer le nouveau classement
                cursor.execute("""
                    INSERT INTO rankings (ranking_date_id, player_id, rank, score)
                    VALUES (?, ?, ?, ?)
                """, (ranking_date_id, player_id, player['rank'], player.get('score', '0')))
                
                logger.debug(f"Joueur {player['name']} ajouté/mis à jour au rang {player['rank']}")
            
            self.conn.commit()
            logger.info(f"Classement {ranking_type} sauvegardé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du classement : {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
    
    def get_player_history(self, player_name: str, limit: int = 7) -> list:
        """Récupère l'historique d'un joueur.
        
        Args:
            player_name: Nom du joueur
            limit: Nombre de jours d'historique (défaut: 7)
            
        Returns:
            Liste des classements du joueur avec date, rang et score
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                WITH avg_ranks AS (
                    SELECT 
                        r2.player_id,
                        rd2.date_j1,
                        AVG(r2.rank) as avg_rank
                    FROM rankings r2
                    JOIN ranking_dates rd2 ON r2.ranking_date_id = rd2.id
                    JOIN players p2 ON r2.player_id = p2.id
                    WHERE p2.name = ?
                    AND rd2.date_j1 >= date(rd2.date_j1, '-30 days')
                    GROUP BY r2.player_id, rd2.date_j1
                )
                SELECT 
                    rd.date_j1 as date,
                    r.rank,
                    r.score,
                    ROUND(avg_r.avg_rank, 1) as avg_rank
                FROM players p
                JOIN rankings r ON r.player_id = p.id
                JOIN ranking_dates rd ON r.ranking_date_id = rd.id
                LEFT JOIN avg_ranks avg_r ON avg_r.date_j1 = rd.date_j1
                WHERE p.name = ?
                ORDER BY rd.date_j1 DESC
                LIMIT ?
            """, (player_name, player_name, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "date": row[0],
                    "rank": row[1],
                    "score": row[2],
                    "avg_rank": row[3] if row[3] is not None else row[1]  # Utiliser le rang actuel si pas de moyenne
                })
                
            return history
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def get_guild_members(self, guild_name: str, ranking_type: str = None):
        """
        Récupère les derniers classements des membres d'une guilde.
        
        Args:
            guild_name (str): Nom de la guilde
            ranking_type (str, optional): Type de classement spécifique
            
        Returns:
            list: Liste des derniers classements des membres
        """
        try:
            cursor = self.conn.cursor()
            
            query = """
                WITH LastRankings AS (
                    SELECT 
                        p.name,
                        p.guild,
                        rd.type,
                        r.rank,
                        r.score,
                        rd.date,
                        ROW_NUMBER() OVER (
                            PARTITION BY p.id, rd.type 
                            ORDER BY rd.date DESC
                        ) as rn
                    FROM players p
                    JOIN rankings r ON p.id = r.player_id
                    JOIN ranking_dates rd ON r.ranking_date_id = rd.id
                    WHERE p.guild = ?
                )
                SELECT name, guild, type, rank, score, date
                FROM LastRankings
                WHERE rn = 1
            """
            
            params = [guild_name]
            if ranking_type:
                query += " AND type = ?"
                params.append(ranking_type)
            
            query += " ORDER BY rank"
            
            cursor.execute(query, params)
            members = cursor.fetchall()
            
            return [{
                'name': row[0],
                'guild': row[1],
                'type': row[2],
                'rank': row[3],
                'score': row[4],
                'date': row[5]
            } for row in members]
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des membres de la guilde : {e}")
            raise
    
    def clear_database(self):
        """Vide complètement la base de données."""
        try:
            cursor = self.conn.cursor()
            
            # Supprimer toutes les données des tables
            cursor.execute("DELETE FROM rankings")
            cursor.execute("DELETE FROM players")
            cursor.execute("DELETE FROM ranking_dates")
            
            # Réinitialiser les compteurs d'auto-incrémentation
            cursor.execute("DELETE FROM sqlite_sequence")
            
            self.conn.commit()
            logger.info("Base de données vidée avec succès")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors du nettoyage de la base de données : {e}")
            raise
    
    def get_latest_ranking(self, limit: int = 100, guild_name: str = None, target_date: datetime = None) -> list:
        """Récupère le classement le plus récent.
        
        Args:
            limit: Nombre maximum de joueurs à retourner
            guild_name: Nom de la guilde à filtrer
            target_date: Date spécifique pour le classement
        """
        try:
            cursor = self.conn.cursor()
            
            # Construction de la requête SQL de base
            query = """
                WITH latest_date AS (
                    SELECT date_j1
                    FROM ranking_dates
                    WHERE type = 'dreamland'
                    {}
                    ORDER BY date_j1 DESC
                    LIMIT 1
                ),
                previous_date AS (
                    SELECT date_j1
                    FROM ranking_dates
                    WHERE type = 'dreamland'
                    AND date_j1 < (SELECT date_j1 FROM latest_date)
                    ORDER BY date_j1 DESC
                    LIMIT 1
                ),
                avg_ranks AS (
                    SELECT 
                        r.player_id,
                        AVG(r.rank) as avg_rank
                    FROM rankings r
                    JOIN ranking_dates rd ON r.ranking_date_id = rd.id
                    WHERE rd.type = 'dreamland'
                    AND rd.date_j1 >= date('now', '-30 days')
                    GROUP BY r.player_id
                )
                SELECT 
                    r.rank,
                    p.name,
                    p.guild,
                    COALESCE(prev_r.rank - r.rank, 0) as rank_change,
                    COALESCE(avg_r.avg_rank, r.rank) as avg_rank
                FROM rankings r
                JOIN ranking_dates rd ON r.ranking_date_id = rd.id
                JOIN players p ON r.player_id = p.id
                LEFT JOIN rankings prev_r ON prev_r.player_id = r.player_id
                    AND prev_r.ranking_date_id = (
                        SELECT id FROM ranking_dates 
                        WHERE date_j1 = (SELECT date_j1 FROM previous_date)
                    )
                LEFT JOIN avg_ranks avg_r ON avg_r.player_id = r.player_id
                WHERE rd.date_j1 = (SELECT date_j1 FROM latest_date)
            """
            
            # Ajout de la condition de date si spécifiée
            date_condition = ""
            if target_date:
                date_condition = f"AND date_j1 = ?"
            
            # Finalisation de la requête avec les filtres
            query = query.format(date_condition)
            
            # Ajout du filtre de guilde si spécifié
            if guild_name:
                query += " AND p.guild LIKE ?"
            
            # Ajout de la limite
            query += " ORDER BY r.rank LIMIT ?"
            
            # Préparation des paramètres
            params = []
            if target_date:
                params.append(target_date.strftime("%Y-%m-%d"))
            if guild_name:
                params.append(f"%{guild_name}%")
            params.append(limit)
            
            # Exécution de la requête
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Conversion en liste de dictionnaires
            players = []
            for row in results:
                players.append({
                    'rank': row[0],
                    'name': row[1],
                    'guild': row[2],
                    'rank_change': row[3],
                    'avg_rank': row[4]
                })
            
            return players
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du classement: {e}")
            raise 