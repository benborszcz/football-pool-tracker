import requests
import re
import datetime
import json

# Define the Team class
class Team:
    def __init__(self, info):
        self.location = info.get('location', 'Unknown Location')
        self.name = info.get('name', 'Unknown Name')
        self.abbreviation = info.get('abbreviation', 'Unknown Abbreviation')
        self.display_name = info.get('displayName', 'Unknown Display Name')
        self.short_display_name = info.get('shortDisplayName', 'Unknown Short Display Name')
        self.score = info.get('score', '0')  # Score is added here for convenience
        self.id = info.get('id', 'Unknown ID')

# Define the Game class
class Game:
    def __init__(self, event):
        self.bowl_name = event.get('competitions', [{}])[0].get('notes', [{}])[0].get('headline', 'Unknown Bowl')
        self.status = event.get('status', {}).get('type', {}).get('description', 'Status Unknown')
        self.display_clock = event.get('status', {}).get('displayClock', '00:00')
        self.period = event.get('status', {}).get('period', 0)
        self.down_distance_text = ''
        self.possession_text = ''
        self.possession = None
        self.competitors = event.get('competitions', [{}])[0].get('competitors', [])
        self.home_team = None
        self.away_team = None
        self.projected_winner = None
        self.projected_loser = None
        self.spread: str = None
        self.over_under = None
        self.winner = None
        self.date_string = event.get('date', 'Unknown Date')
        self.date = datetime.datetime.strptime(self.date_string, "%Y-%m-%dT%H:%MZ")
        self.picks = 0
        self.probabilities = None

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
        self.probabilities = event.get('competitions', [{}])[0].get('situation', {}).get('lastPlay', {}).get('probability', None)

        if odds_info and odds_info[0]:
            odds_info = odds_info[0]  # Assuming the first odds info is what we want
            self.spread = odds_info.get('spread')
            self.over_under = odds_info.get('overUnder')

            # Extract the projected winner from the details field
            details = odds_info.get('details', '')
            match = re.search(r'([A-Z&]+) -?\d+(\.\d+)?', details)
            
            if match:
                winner_abbreviation = match.group(1)
                # Determine the projected winner based on the abbreviation
                if self.home_team.abbreviation == winner_abbreviation:
                    self.projected_winner = self.home_team
                    self.projected_loser = self.away_team
                elif self.away_team.abbreviation == winner_abbreviation:
                    self.projected_winner = self.away_team
                    self.projected_loser = self.home_team
                    #self.spread = -self.spread  # Flip the spread if the away team is the projected winner
        elif self.probabilities:
            print(self.probabilities)
            if self.probabilities['homeWinPercentage'] > self.probabilities['awayWinPercentage']:
                print(self.probabilities['homeWinPercentage'])
                self.projected_winner = self.home_team
                self.projected_loser = self.away_team
            else:
                self.projected_winner = self.away_team
                self.projected_loser = self.home_team
        elif self.status == "In Progress":
            home_score = int(self.home_team.score) ** (1.7+self.period/10)
            away_score = int(self.away_team.score) ** (1.7+self.period/10)

            total_score = home_score + away_score

            if total_score == 0:
                self.probabilities = {
                    'homeWinPercentage': 0.51,
                    'awayWinPercentage': 0.49
                }
            else:
                home_win_percentage = (home_score / total_score)
                away_win_percentage = (away_score / total_score)

                self.probabilities = {
                    'homeWinPercentage': home_win_percentage,
                    'awayWinPercentage': away_win_percentage
                }
            if self.probabilities['homeWinPercentage'] > self.probabilities['awayWinPercentage']:
                self.projected_winner = self.home_team
                self.projected_loser = self.away_team
            else:
                self.projected_winner = self.away_team
                self.projected_loser = self.home_team
            

        # Extract situation information if the game is not final
        if self.status != 'Final':
            situation = event.get('competitions', [{}])[0].get('situation', {})
            self.down_distance_text = situation.get('downDistanceText', '')
            possession_id = situation.get('lastPlay', {}).get('team', {}).get('id', None)
            if possession_id == self.home_team.id:
                self.possession = self.home_team
            else:
                self.possession = self.away_team
        else:
            if self.home_team.abbreviation == "MEM":
                self.winner = self.home_team
            else:
                self.winner = self.home_team if int(self.home_team.score) > int(self.away_team.score) else self.away_team

    def set_picks(self, picks):
        self.picks = picks

    def __str__(self):
        return f"**{self.status}** {self.bowl_name}: {self.home_team.location}({self.home_team.abbreviation}) {self.home_team.score} vs. {self.away_team.location}({self.away_team.abbreviation}) {self.away_team.score}"

# Function to fetch events and create Game objects
# ...

def fetch_games():
    url = 'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard'
    response = requests.get(url)
    data = response.json()
    # Save games to a file
    with open('games3.json', 'w') as file:
        json.dump(data, file, indent=4)
    
    events = data.get('events', [])
    games = []
    for event in events:
        game = Game(event)
        games.append(game)
    
    # Sort the games by date
    games.sort(key=lambda x: x.date)

    # Save games to a file
    with open('games2.txt', 'w', encoding='utf-8') as file:
        for game in games:
            file.write(str(game) + '\n')
    
    return games