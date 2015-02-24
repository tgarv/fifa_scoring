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

    def compute_stats(self):
        player_results = {}
        team_results = {}
        for model in self.models:
            winning_players = []
            losing_players = []
            tying_players = []
            if model.home_score > model.away_score:
                winning_players = model.home_players
                losing_players = model.away_players
            elif model.home_score < model.away_score:
                winning_players = model.away_players
                losing_players = model.home_players
            elif model.home_score == model.away_score:
                tying_players = model.home_players + model.away_players

            # Add in results for wins/losses/ties
            for player in winning_players:
                if player not in player_results:
                    player_results[player] = {'wins': 0, 'losses': 0, 'ties': 0, 'goals': 0, 'goals_against': 0}
                player_results[player]['wins'] += 1

            for player in losing_players:
                if player not in player_results:
                    player_results[player] = {'wins': 0, 'losses': 0, 'ties': 0, 'goals': 0, 'goals_against': 0}
                player_results[player]['losses'] += 1

            for player in tying_players:
                if player not in player_results:
                    player_results[player] = {'wins': 0, 'losses': 0, 'ties': 0, 'goals': 0, 'goals_against': 0}
                player_results[player]['ties'] += 1

            # Add in score for and against
            for player in model.home_players:
                player_results[player]['goals'] += model.home_score
                player_results[player]['goals_against'] += model.away_score

            for player in model.away_players:
                player_results[player]['goals'] += model.away_score
                player_results[player]['goals_against'] += model.home_score

        for player, stats in player_results.iteritems():
            total_games = stats['wins'] + stats['losses'] + stats['ties']
            winning_percentage = float(stats['wins']) / total_games
            goals_per_game = float(stats['goals']) / total_games
            goals_against_per_game = float(stats['goals_against']) / total_games
            goal_differential = float(stats['goals'] - stats['goals_against'])
            goal_differential_per_game = float(goal_differential) / total_games

            player_results[player]['total_games']                = total_games
            player_results[player]['winning_percentage']         = winning_percentage
            player_results[player]['goals_per_game']             = goals_per_game
            player_results[player]['goals_against_per_game']     = goals_against_per_game
            player_results[player]['goal_differential']          = goal_differential
            player_results[player]['goal_differential_per_game'] = goal_differential_per_game


        print player_results
        return player_results