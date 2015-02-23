from flask_app.models.game_model import GameModel

class GameCollection():
    def __init__(self):
        self.models = []

    def populate(self, data):
        for datum in data:
            g = GameModel()
            g.populate(datum)
            self.models.append(g)