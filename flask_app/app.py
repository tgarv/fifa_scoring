from flask import Flask, render_template
import os
import sqlite3
import queries
import json

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
        return render_template('index.html', player_results=player_results, team_results=team_results)
        return json.dumps({'player_results': str(player_results), 'team_results': str(team_results)})

    def get_cursor():
        return sqlite3.connect('/home/ubuntu/workspace/scores.db').cursor()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))