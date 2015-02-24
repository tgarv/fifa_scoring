from flask_app.models.game_model import GameModel

class GameCollection():
    def __init__(self, models=[]):
        self.models = models

    def populate(self, data):
        for datum in data:
            g = GameModel()
            g.populate(datum)
            if g.away_players:
                # These come back as '/'-delimited strings, so split them into arrays
                g.away_players = g.away_players.split('/')
                g.home_players = g.home_players.split('/')
            self.models.append(g)

    # Returns a new collection made up of the models in this collection that meet a certain criteria.
    # If exclusive is True, we'll look for games that have all of the players in players and no other players.
    # If exclusive is False, we'll look for games that have all of the players in players and possibly others
    # e.g. if you want all games that 'Bob' played in, use exclusive = False. If you only want all games that featured
    # 'Bob', 'Jon', and 'Tom' (and no other players), use exclusive = True
    def filter_by_players(self, players, exclusive=True):
        players_set = set(players)
        new_models = []

        for model in self.models:
            game_players_set = set(model.home_players + model.away_players)
            if exclusive:
                if game_players_set == players_set:
                    new_models.append(model)
            else:
                if players_set.issubset(game_players_set):
                    new_models.append(model)

        return GameCollection(new_models)
