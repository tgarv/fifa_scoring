from flask_app.models.game_model import GameModel
import datetime

class GameCollection():
    def __init__(self):
        self.models = []

    def populate(self, data):
        for datum in data:
            g = GameModel()
            g.populate(datum)
            # These come back as '/'-delimited strings, so split them into arrays
            if g.away_players:
                g.away_players = g.away_players.split('/')
            if g.home_players:
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

        c = GameCollection()
        c.models = new_models
        return c

    def compute_player_stats(self):
        player_results = {}
        team_results = {}

        player_names = set()
        team_names = set()

        for model in self.models:
            for player in model.home_players + model.away_players:
                player_names.add(player)
            team_names.add(','.join(sorted(model.away_players)))
            team_names.add(','.join(sorted(model.home_players)))

        for name in team_names:
            team_results[name] = {'name': name, 'wins': 0, 'losses': 0, 'ties': 0, 'goals': 0, 'goals_against': 0}

        for name in player_names:
            player_results[name] = {'name': name, 'wins': 0, 'losses': 0, 'ties': 0, 'goals': 0, 'goals_against': 0}

        for model in self.models:
            winning_players = []
            losing_players = []
            tying_teams = []
            if model.home_score > model.away_score:
                winning_players = model.home_players
                losing_players = model.away_players
            elif model.home_score < model.away_score:
                winning_players = model.away_players
                losing_players = model.home_players
            elif model.home_score == model.away_score:
                tying_teams = [model.home_players, model.away_players]

            # Add in results for wins/losses/ties
            for player in winning_players:
                player_results[player]['wins'] += 1

            for player in losing_players:
                player_results[player]['losses'] += 1

            for team in tying_teams:
                for player in team:
                    player_results[player]['ties'] += 1

            # Add in score for and against
            for player in model.home_players:
                player_results[player]['goals'] += model.home_score
                player_results[player]['goals_against'] += model.away_score

            for player in model.away_players:
                player_results[player]['goals'] += model.away_score
                player_results[player]['goals_against'] += model.home_score

            # Now the same stats for teams
            winning_team_name = ','.join(sorted(winning_players))
            losing_team_name = ','.join(sorted(losing_players))
            if winning_team_name:
                team_results[winning_team_name]['wins'] += 1
            if losing_team_name:
                team_results[losing_team_name]['losses'] += 1

            for team in tying_teams:
                tying_team_name = ','.join(sorted(team))
                team_results[tying_team_name]['ties'] += 1

            away_team_name = ','.join(sorted(model.away_players))
            home_team_name = ','.join(sorted(model.home_players))

            team_results[away_team_name]['goals'] += model.away_score
            team_results[away_team_name]['goals_against'] += model.home_score
            team_results[home_team_name]['goals'] += model.home_score
            team_results[home_team_name]['goals_against'] += model.away_score

        # Now compute some aggregate stats like goals per game etc.
        for group in [team_results, player_results]:
            for name, stats in group.iteritems():
                total_games = stats['wins'] + stats['losses'] + stats['ties']
                winning_percentage = float(stats['wins']) / total_games
                goals_per_game = float(stats['goals']) / total_games
                goals_against_per_game = float(stats['goals_against']) / total_games
                goal_differential = stats['goals'] - stats['goals_against']
                goal_differential_per_game = float(goal_differential) / total_games

                group[name]['total_games']                = total_games
                group[name]['winning_percentage']         = winning_percentage
                group[name]['goals_per_game']             = goals_per_game
                group[name]['goals_against_per_game']     = goals_against_per_game
                group[name]['goal_differential']          = goal_differential
                group[name]['goal_differential_per_game'] = goal_differential_per_game

        player_results_list = []
        team_results_list = []
        for item in player_results.values():
            player_results_list.append(item)

        for item in team_results.values():
            team_results_list.append(item)

        return {'player_stats': player_results_list, 'team_stats': team_results_list}

    def filter_by_date(self, start_date='0', end_date='Z'):
        new_models = []
        for model in self.models:
            if model.date >= start_date and model.date < end_date:
                new_models.append(model)

        gc = GameCollection()
        gc.models = new_models
        return gc

    def get_weekly_stats(self):
        weekly_stats = []
        today = datetime.date.today()
        start_date = today + datetime.timedelta(days=(0-today.weekday()))
        start_date_string = start_date.isoformat()
        end_date = None
        end_date_string = 'Z'

        new_collection = self.filter_by_date(start_date_string, end_date_string)
        stats = new_collection.compute_player_stats()
        weekly_stats.append({'start_date': start_date_string, 'end_date': 'Now', 'stats': stats})

        for i in xrange(6): #6 weeks
            end_date = start_date
            start_date = start_date - datetime.timedelta(days=7)
            end_date_string = end_date.isoformat()
            start_date_string = start_date.isoformat()
            new_collection = self.filter_by_date(start_date_string, end_date_string)
            stats = new_collection.compute_player_stats()

            weekly_stats.append({'start_date': start_date_string, 'end_date': end_date_string, 'stats': stats})

        # Go from past to present
        weekly_stats = weekly_stats[::-1]
        return weekly_stats