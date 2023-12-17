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
            team = None
            if game.bowl_name == 'CFP National Championship Pres. by AT&T':
                team = find_team_by_abbreviation(self.picks[-2].game, pick['team'])
                if team is None:
                    team = find_team_by_abbreviation(self.picks[-1].game, pick['team'])
            else:
                team = find_team_by_abbreviation(game, pick['team'])
            self.picks.append(Pick(game, team))
    
    
    def analyze_picks(self, games):
        for pick in self.picks:
            if pick.team is None: 
                continue
            if pick.game and pick.game.winner:
                pick.correct = pick.game.winner.abbreviation == pick.team.abbreviation

    def calculate_streak(self):
        streak_type = None
        streak_count = 0
        for pick in reversed(self.picks):
            if pick.correct is None:  # Skip games without a result
                continue
            if streak_type is None:
                streak_type = 'W' if pick.correct else 'L'
                streak_count = 1
            elif ((pick.correct and streak_type == 'W') or
                  (not pick.correct and streak_type == 'L')):
                streak_count += 1
            else:
                break  # Streak ended
        return f"{streak_type}{streak_count}" if streak_count > 0 else ""

class Pick:
    def __init__(self, game, team):
        self.game = game
        self.team = team
        self.correct: bool = None