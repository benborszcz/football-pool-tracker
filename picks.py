class Picks:
    def __init__(self, name, data, games):
        self.name = name
        self.picks: list[Pick] = []
        self.parse_picks(data, games)

    def parse_picks(self, data, games):
        def find_game_by_name(games, name):
            for game in games:
                if game.bowl_name == name:
                    return game
            return None
        
        def find_team_by_abbreviation(game, abbreviation):
            if abbreviation == game.home_team.abbreviation:
                return game.home_team
            elif abbreviation == game.away_team.abbreviation:
                return game.away_team
            else:
                return None
    
        for pick in data:
            game = find_game_by_name(games, pick['game'])
            if game is None:
                print(f"Unable to find game: {pick['game']}")
                continue
            team = find_team_by_abbreviation(game, pick['team'])
            self.picks.append(Pick(game, team))
    
    
    def analyze_picks(self, games):
        for pick in self.picks:
            if pick.team is None: 
                pick.correct = False
                continue
            if pick.game and pick.game.winner:
                pick.correct = pick.game.winner.abbreviation == pick.team.abbreviation

class Pick:
    def __init__(self, game, team):
        self.game = game
        self.team = team
        self.correct: bool = None