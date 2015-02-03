from flask import Flask, render_template, request, redirect, url_for
import os
import queries
import json
import MySQLdb as db

def create_app(settings_key='dev'):
    app = Flask(__name__)
    app.debug = True
    # app.config.from_object('config')

    @app.route('/test')
    def test():
        return 'Testing'

    @app.route('/')
    def main():
        cursor = get_cursor()
        cursor.execute(queries.player_game_results_query)
        player_results = cursor.fetchall()
        cursor.execute(queries.team_results_query)
        team_results = cursor.fetchall();
        cursor.execute(queries.game_history_query)
        game_history = cursor.fetchall()
        game_history = deduplicate_game_players(game_history)
        print game_history
        return render_template('index.html', player_results=player_results, team_results=team_results, game_history=game_history)
        return json.dumps({'player_results': str(player_results), 'team_results': str(team_results)})

    @app.route('/add_game', methods=['POST'])
    def add_game():
        print request.form
        conn = get_connection()
        cursor = conn.cursor()
        # print (request.form['date'], request.form['away_team'], request.form['home_team'], request.form['away_score'], request.form['home_score'], request.form['half_length'])
        sql = "INSERT INTO game (date, away_team, home_team, away_score, home_score, half_length) VALUES (?, ?, ?, ?, ?, ?);"
        cursor.execute(sql, (request.form['date'], request.form['away_team'], request.form['home_team'], request.form['away_score'], request.form['home_score'], request.form['half_length']))
        game_id = cursor.lastrowid
        away_players = request.form['away_players'].split(',')
        for player in away_players:
            sql = "INSERT INTO away_players (game_id, player_name) VALUES (%s, %s)";
            cursor.execute(sql, (game_id, player))
        home_players = request.form['home_players'].split(',')
        for player in home_players:
            sql = "INSERT INTO home_players (game_id, player_name) VALUES (%s, %s)";
            cursor.execute(sql, (game_id, player))
        conn.commit()
        return main()

    def get_connection():
        return db.connect('us-cdbr-iron-east-01.cleardb.net', 'b6a8bbd0db6ff6', '02c55634', 'heroku_4257da2e9f87a35')

    def get_cursor():
        return get_connection().cursor()

    def deduplicate_game_players(game_history):
        return_value = []
        for game in game_history:
            game_dict = {
                'date': game[0],
                'home_players': game[1],
                'home_team': game[2],
                'home_score': game[3],
                'away_players': game[4],
                'away_team': game[5],
                'away_score': game[6]
                }

            home_players = game[1]
            away_players = game[4]
            # Turn these into sets to deduplicate the names.
            # This is obviously a hack, I should actually fix the query.
            home_players = set(home_players.split('-'))
            away_players = set(away_players.split('-'))
            game_dict['home_players'] = '/'.join(home_players)
            game_dict['away_players'] = '/'.join(away_players)
            return_value.append(game_dict)
        return return_value

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)