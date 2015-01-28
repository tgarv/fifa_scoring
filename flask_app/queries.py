total_goals_query = """SELECT name, SUM(score) FROM (SELECT player_name as name, home_score as score FROM home_players INNER JOIN game ON game_id = id UNION ALL SELECT player_name as name, away_score as score FROM away_players INNER JOIN game ON game_id = id) GROUP BY name"""
team_goals_query = """
SELECT team_players, SUM(score), AVG(score), COUNT(score)
FROM 
    (SELECT group_concat(player_name, '-') as team_players,
            away_score as score
    FROM 
        (SELECT player_name, game_id
         FROM away_players ORDER BY player_name
        )
    INNER JOIN game 
        ON game_id = id
    GROUP BY game_id
    UNION ALL 
    SELECT group_concat(player_name, '-') as team_players,
           home_score as score
    FROM 
        (SELECT player_name, game_id
         FROM home_players ORDER BY player_name
        )
    INNER JOIN game
        ON game_id = id
    GROUP BY game_id)
GROUP BY team_players;"""

player_wins_query = """SELECT name, COUNT(*) FROM (SELECT player_name as name, home_score as score FROM home_players INNER JOIN game ON game_id = id WHERE home_score > away_score UNION ALL SELECT player_name as name, away_score as score FROM away_players INNER JOIN game ON game_id = id WHERE away_score > home_score) GROUP BY name;"""
player_game_results_query = """SELECT name, SUM(win) as wins, SUM(loss) as losses, SUM(tie) as ties FROM (SELECT player_name as name, home_score as score, home_score > away_score as win, home_score < away_score as loss, home_score = away_score as tie FROM home_players INNER JOIN game ON game_id = id UNION ALL SELECT player_name as name, away_score as score, away_score > home_score as win, away_score < home_score as loss, away_score = home_score as tie FROM away_players INNER JOIN game ON game_id = id) GROUP BY name;"""
team_results_query = """
SELECT team_players, SUM(win) as wins, SUM(loss) as losses, SUM(tie) as ties
FROM 
    (SELECT group_concat(player_name, '-') as team_players,
            away_score as score,
            away_score > home_score as win,
            away_score = home_score as tie,
            away_score < home_score as loss
    FROM 
        (SELECT player_name, game_id
         FROM away_players ORDER BY player_name
        )
    INNER JOIN game 
        ON game_id = id
    GROUP BY game_id
    UNION ALL 
    SELECT group_concat(player_name, '-') as team_players,
           home_score as score,
           home_score > away_score as win,
           home_score = away_score as tie,
           home_score < away_score as loss
    FROM 
        (SELECT player_name, game_id
         FROM home_players ORDER BY player_name
        )
    INNER JOIN game
        ON game_id = id
    GROUP BY game_id)
GROUP BY team_players;"""