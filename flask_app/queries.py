total_goals_query = """SELECT name, SUM(score) FROM (SELECT player_name as name, home_score as score FROM home_players INNER JOIN game ON game_id = id UNION ALL SELECT player_name as name, away_score as score FROM away_players INNER JOIN game ON game_id = id) GROUP BY name"""
team_goals_query = """
SELECT team_players, SUM(score), AVG(score), COUNT(score)
FROM
    (SELECT group_concat(player_name SEPARATOR '-') as team_players,
            away_score as score
    FROM
        (SELECT player_name, game_id
         FROM away_players ORDER BY player_name
        ) ap
    INNER JOIN game
        ON game_id = id
    GROUP BY game_id
    UNION ALL
    SELECT group_concat(player_name SEPARATOR '-') as team_players,
           home_score as score
    FROM
        (SELECT player_name, game_id
         FROM home_players ORDER BY player_name
        ) hp
    INNER JOIN game
        ON game_id = id
    GROUP BY game_id) p
GROUP BY team_players;"""

player_wins_query = """SELECT name, COUNT(*)FROM (SELECT player_name as name, home_score as score FROM home_players INNER JOIN game ON game_id = id WHERE home_score > away_score UNION ALL SELECT player_name as name, away_score as score FROM away_players INNER JOIN game ON game_id = id WHERE away_score > home_score) GROUP BY name;"""
player_game_results_query = """
SELECT  name,
        COUNT(*) as games_played,
        SUM(win) as wins,
        SUM(loss) as losses,
        SUM(tie) as ties,
        SUM(score),
        AVG(score),
        SUM(opponent_score),
        AVG(opponent_score),
        SUM(score) - SUM(opponent_score) as goal_differential,
        (SUM(score) - SUM(opponent_score)) * 1.0 / COUNT(*) as average_goal_differential
FROM
    (SELECT player_name as name,
            home_score as score,
            away_score as opponent_score,
            home_score > away_score as win,
            home_score < away_score as loss,
            home_score = away_score as tie
     FROM home_players
     INNER JOIN game
        ON game_id = id
    UNION ALL
     SELECT player_name as name,
            away_score as score,
            home_score as opponent_score,
            away_score > home_score as win,
            away_score < home_score as loss,
            away_score = home_score as tie
     FROM away_players
     INNER JOIN game
        ON game_id = id
    ) p GROUP BY name;"""
team_results_query = """
SELECT  team_players,
        COUNT(*) as games_played,
        SUM(win) as wins,
        SUM(loss) as losses,
        SUM(tie) as ties,
        SUM(score) as score,
        AVG(score) as average_score,
        SUM(opponent_score) as opponent_score,
        AVG(opponent_score) as average_opponent_score,
        SUM(score) - SUM(opponent_score) as goal_differential,
        (SUM(score) - SUM(opponent_score)) * 1.0 / COUNT(*) as average_goal_differential
FROM
    (SELECT group_concat(player_name SEPARATOR '-') as team_players,
            away_score as score,
            home_score as opponent_score,
            away_score > home_score as win,
            away_score = home_score as tie,
            away_score < home_score as loss
    FROM
        (SELECT player_name, game_id
         FROM away_players ORDER BY player_name
        ) ap
    INNER JOIN game
        ON game_id = id
    GROUP BY game_id
    UNION ALL
    SELECT group_concat(player_name SEPARATOR '-') as team_players,
           home_score as score,
           away_score as opponent_score,
           home_score > away_score as win,
           home_score = away_score as tie,
           home_score < away_score as loss
    FROM
        (SELECT player_name, game_id
         FROM home_players ORDER BY player_name
        ) hp
    INNER JOIN game
        ON game_id = id
    GROUP BY game_id) p
GROUP BY team_players;"""


# TODO this query isn't correct -- the multiple inner joins cause duplication of player names
# but I'm fixing it in the python code
game_history_query = """SELECT date, group_concat(hp.player_name SEPARATOR '-'), home_team, home_score, group_concat(ap.player_name SEPARATOR '-'), away_team, away_score FROM game INNER JOIN away_players ap ON ap.game_id = id INNER JOIN home_players hp ON hp.game_id = id GROUP BY id ORDER BY date DESC;"""