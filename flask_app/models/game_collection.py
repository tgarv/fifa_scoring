from flask_app.models.game_model import GameModel

class GameCollection():
    def __init__(self):
        self.models = []

    def populate(self, data):
        for datum in data:
            g = GameModel()
            g.populate(datum)
            if g.away_players:
                # These come back as '/'-delimited strings, so split them into arrays
                g.away_players = g.away_players.split('/')
                g.home_players = g.home_players.split('/')
            self.models.append(g)