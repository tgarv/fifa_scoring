from flask import Flask, render_template, request, redirect, url_for
import os
import queries
import json
import MySQLdb as db
import MySQLdb.cursors
from datetime import date
from flask_app.models.game_collection import GameCollection

def create_app(settings_key='dev'):
    app = Flask(__name__)
    app.debug = True
    # app.config.from_object('config')

    @app.route('/')
    def main():
        start_date = request.args.get('start_date', '0')
        end_date = request.args.get('end_date', 'Z')
        all_players = request.args.get('all_players', False)
        cursor = get_cursor()

        cursor.execute(queries.team_results_query, (start_date, end_date))
        team_results = cursor.fetchall();
        cursor.execute(queries.game_history_query, (start_date, end_date))
        game_history = cursor.fetchall()
        game_history = deduplicate_game_players(game_history)
        gc = GameCollection()
        gc.populate(game_history)
        if all_players:
            gc = gc.filter_by_players(['DT','Jon','Alistair','CT'], True, True)
        # print len(gc.filter_by_players(['DT','Jon','Alistair','CT']).models)
        # print len(gc.filter_by_players(['DT','Jon','Alistair']).models)
        # print len(gc.filter_by_players(['CT'], False).models)
        # print len(gc.filter_by_players(['Jon', 'CT'], False).models)
        if request.args.get('unique_teams', False):
            gc = gc.remove_duplicate_club_games()
        stats = gc.compute_player_stats()

        return render_template('index.html', player_results=stats['player_stats'], team_results=stats['team_stats'], club_results=stats['club_stats'], game_history=gc)

    @app.route('/get_weekly_stats')
    def get_weekly_stats():
        start_date = request.args.get('start_date', '0')
        end_date = request.args.get('end_date', 'Z')
        weeks = int(request.args.get('weeks', 6))
        cursor = get_cursor()
        cursor.execute(queries.game_history_query, (start_date, end_date))
        game_history = cursor.fetchall()
        game_history = deduplicate_game_players(game_history)
        gc = GameCollection()
        gc.populate(game_history)
        print request.args
        if request.args.get('all_players', False):
            gc = gc.filter_by_players(['DT','Jon','Alistair','CT'], True, True)

        return json.dumps(gc.get_weekly_stats(weeks))

    @app.route('/add_game', methods=['POST'])
    def add_game():
        conn = get_connection()
        cursor = conn.cursor()
        # print (request.form['date'], request.form['away_team'], request.form['home_team'], request.form['away_score'], request.form['home_score'], request.form['half_length'])
        sql = "INSERT INTO game (date, away_team, home_team, away_score, home_score, half_length) VALUES (%s, %s, %s, %s, %s, %s);"
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

    @app.route('/test')
    def test():
        weeks = int(request.args.get('weeks', 6))
        return render_template('test.html', all_players=request.args.get('all_players', False), weeks=weeks)

    def get_connection():
        return db.connect('us-cdbr-iron-east-01.cleardb.net', 'b6a8bbd0db6ff6', '02c55634', 'heroku_4257da2e9f87a35', cursorclass=MySQLdb.cursors.DictCursor)

    def get_cursor():
        return get_connection().cursor()

    def get_first_day_of_week():
        today = date.today()
        return today + datetime.timedelta(days=(0-today.weekday()))

    def deduplicate_game_players(game_history):
        return_value = []
        for game in game_history:
            game_dict = {
                'date': game['date'],
                'home_players': game['home_players'],
                'home_team': game['home_team'],
                'home_score': game['home_score'],
                'away_players': game['away_players'],
                'away_team': game['away_team'],
                'away_score': game['away_score']
                }

            home_players = game['home_players']
            away_players = game['away_players']
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