import requests
import re

# Define the Team class
class Team:
    def __init__(self, info):
        self.location = info.get('location', 'Unknown Location')
        self.name = info.get('name', 'Unknown Name')
        self.abbreviation = info.get('abbreviation', 'Unknown Abbreviation')
        self.display_name = info.get('displayName', 'Unknown Display Name')
        self.short_display_name = info.get('shortDisplayName', 'Unknown Short Display Name')
        self.score = info.get('score', '0')  # Score is added here for convenience

# Define the Game class
class Game:
    def __init__(self, event):
        self.bowl_name = event.get('competitions', [{}])[0].get('notes', [{}])[0].get('headline', 'Unknown Bowl')
        self.status = event.get('status', {}).get('type', {}).get('description', 'Status Unknown')
        self.display_clock = event.get('status', {}).get('displayClock', '00:00')
        self.period = event.get('status', {}).get('period', 0)
        self.down_distance_text = ''
        self.possession_text = ''
        self.competitors = event.get('competitions', [{}])[0].get('competitors', [])
        self.home_team = None
        self.away_team = None
        self.projected_winner = None
        self.spread = None
        self.over_under = None

        # Create Team objects for home and away teams
        for team_info in self.competitors:
            team = Team(team_info.get('team', {}))
            team.score = team_info.get('score', '0')  # Add the score to the team object
            if team_info.get('homeAway') == 'home':
                self.home_team = team
            elif team_info.get('homeAway') == 'away':
                self.away_team = team

        # Extract odds information
        odds_info = event.get('competitions', [{}])[0].get('odds', [{}])
        if odds_info:
            odds_info = odds_info[0]  # Assuming the first odds info is what we want
            self.spread = odds_info.get('spread')
            self.over_under = odds_info.get('overUnder')

            # Extract the projected winner from the details field
            details = odds_info.get('details', '')
            match = re.search(r'([A-Z]+) -?\d+(\.\d+)?', details)
            if match:
                winner_abbreviation = match.group(1)
                # Determine the projected winner based on the abbreviation
                if self.home_team.abbreviation == winner_abbreviation:
                    self.projected_winner = self.home_team
                elif self.away_team.abbreviation == winner_abbreviation:
                    self.projected_winner = self.away_team

        # Extract situation information if the game is not final
        if self.status != 'Final':
            situation = event.get('competitions', [{}])[0].get('situation', {})
            self.down_distance_text = situation.get('downDistanceText', '')
            self.possession_text = situation.get('possessionText', '')

# Function to fetch events and create Game objects
def fetch_games():
    url = 'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard'
    response = requests.get(url)
    data = response.json()
    events = data.get('events', [])
    games = []
    for event in events:
        game = Game(event)
        games.append(game)
    
    return games

# Fetch the games and create Game objects
games = fetch_games()

# Example usage: Print out the bowl names, team names/scores, status, and odds information
for game in games:
    projected_winner = game.projected_winner.display_name if game.projected_winner else "N/A"
    print(f"{game.bowl_name}: {game.home_team.location} {game.home_team.score} vs. {game.away_team.location} {game.away_team.score}")
    print(f"Status: {game.status}, Time: {game.display_clock}, Period: {game.period}")
    print(f"Down & Distance: {game.down_distance_text}, Possession: {game.possession_text}")
    print(f"Projected Winner: {projected_winner}, Spread: {game.spread}, Over/Under: {game.over_under}")
    print("-" * 40)