from flask import Flask, jsonify
import csv
import os
from data_retrieval import fetch_games, Team, Game
from picks import Picks  
import math
import numpy as np
import random
app = Flask(__name__)

from flask import Flask, jsonify, render_template
import os

# Function to read picks from CSV files
def read_picks_from_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        picks_data = list(reader)
    return picks_data

# Function to load all picks
def load_all_picks(games):
    picks_folder = 'picks'
    all_picks = {}
    for file_name in os.listdir(picks_folder):
        if file_name.endswith('_picks.csv'):
            name = file_name.replace('_picks.csv', '').replace('_', ' ').title()
            file_path = os.path.join(picks_folder, file_name)
            picks_data = read_picks_from_csv(file_path)
            all_picks[name] = Picks(name, picks_data, games)
    return all_picks

def game_to_json(game):
    return {
        'bowl_name': game.bowl_name,
        'status': game.status,
        'display_clock': game.display_clock,
        'period': game.period,
        'home_team': {
            'location': game.home_team.location,
            'name': game.home_team.name,
            'abbreviation': game.home_team.abbreviation,
            'display_name': game.home_team.display_name,
            'short_display_name': game.home_team.short_display_name,
            'score': game.home_team.score,
        },
        'away_team': {
            'location': game.away_team.location,
            'name': game.away_team.name,
            'abbreviation': game.away_team.abbreviation,
            'display_name': game.away_team.display_name,
            'short_display_name': game.away_team.short_display_name,
            'score': game.away_team.score,
        },
        'down_distance_text': game.down_distance_text,
        'possession_text': game.possession_text,
        'possession': game.possession.abbreviation if game.possession else None,
        'winner': game.winner.abbreviation if game.winner else None,
        'probabilities': {
            'homeWinPercentage': game.probabilities['homeWinPercentage'] if game.probabilities else None,
            'awayWinPercentage': game.probabilities['awayWinPercentage'] if game.probabilities else None,
        }
    }

def calculate_winner_percentage(game):
    if game.spread is None:
        if game.probabilities is not None:
            probs = 0
            if game.probabilities['homeWinPercentage'] > game.probabilities['awayWinPercentage']:
                probs = game.probabilities['homeWinPercentage']
            else:
                probs = game.probabilities['awayWinPercentage']
            return probs * 100
        return None  # If there's no spread, we can't calculate a percentage
    spread = float(game.spread)
    sigma = 15  # Adjust this value based on the sportsbook's assessment
    spread = -spread
    if game.projected_winner is None: return None
    percentage = 1 / (1 + math.exp(-spread / sigma))
    ret = (1 - percentage) * 100
    if game.projected_winner == game.home_team:
        ret = percentage * 100
    #print(f"Game: {game.bowl_name},Spread: {spread}, {game.projected_winner.abbreviation} Percentage: {ret}")

    return ret
    

def count_picks_for_team(team, games):
    # Load all picks from the CSV files (assuming this is how you store picks)
    all_picks = load_all_picks(games)
    count = 0
    for picks in all_picks.values():
        for pick in picks.picks:
            if pick.team and pick.team.abbreviation == team.abbreviation:
                count += 1
    return count

from concurrent.futures import ThreadPoolExecutor


import numpy as np

def simulate_win_probabilities(all_picks, games_dict, num_simulations=2000):

    random.seed(42)
    np.random.seed(42)

    names = list(all_picks.keys())
    champion_counts = {name: 0 for name in names} # Dictionary to track total wins for each name
    
    win_percentages = np.array([calculate_winner_percentage(game) if calculate_winner_percentage(game) is not None else -1 for game in games_dict.values()])
    
    # Pre-calculate the pick arrays and the number of correct picks
    pick_arrays = {name: np.array(all_picks[name].pick_array) for name in names}
    correct_picks = {name: all_picks[name].calculate_correct_picks() for name in names}
    max_wins = 0
    for i in range(num_simulations):
        random_array = np.random.rand(len(win_percentages))*100
        valid_indices = win_percentages != -1
        win_percentages = win_percentages[valid_indices]
        random_array = random_array[valid_indices]
        pick_arrays = {name: pick_arrays[name][valid_indices] for name in names}

        results = np.where(np.logical_and(win_percentages > 0, random_array < np.array(win_percentages)), 1, 0)

        if i == 1:
            #print(win_percentages)
            #print(random_array)
            #print(results)
            pass
        # Use numpy's broadcasting feature to calculate the outcomes and count the zeros and twos for all names at once
        outcomes = np.array([pick_arrays[name] + results for name in names])
        win_counts = np.count_nonzero(outcomes == 0, axis=1) + np.count_nonzero(outcomes == 2, axis=1)

        # Add the number of correct picks to the win counts
        win_counts += np.array([correct_picks[name] for name in names])

        # Function to simulate the championship game
        def simulate_championship_game(all_picks, games_dict, results):
            # Get the winners of the last two games
            last_two_games = list(games_dict.values())[-3:-1]
            winner1 = results[-2]
            winner2 = results[-1]
            
            if results[-2] == 1:
                winner1 = last_two_games[0].projected_winner
            elif results[-2] == 0:
                winner1 = last_two_games[0].projected_loser
            
            if results[-1] == 1:
                winner2 = last_two_games[1].projected_winner
            elif results[-1] == 0:
                winner2 = last_two_games[1].projected_loser

            odds = 0
            if winner1.abbreviation == "ALA" and winner2.abbreviation == "TEX":
                odds = 0.53
            elif winner1.abbreviation == "ALA" and winner2.abbreviation == "WASH":
                odds = 0.70
            elif winner1.abbreviation == "MICH" and winner2.abbreviation == "TEX":
                odds = 0.58
            elif winner1.abbreviation == "MICH" and winner2.abbreviation == "WASH":
                odds = 0.72

            winner = winner2
            if random.random() < odds:
                winner = winner1

            win_counts = {name: 0 for name in names}
            for name, picks in all_picks.items():
                for pick in picks.picks:
                    if pick.game.bowl_name == "CFP National Championship Pres. by AT&T":
                        if pick.game.winner == winner:
                            win_counts[name] += 1

            return win_counts

        # Simulate the championship game
        championship_win_counts = simulate_championship_game(all_picks, games_dict, results)

        # Add the championship win counts to the total win counts
        for name in names:
            win_counts[names.index(name)] += championship_win_counts[name]
            

        # Use numpy's argmax function to find the index of the maximum win count
        max_wins_indices = np.argwhere(win_counts == np.amax(win_counts)).flatten()

        # If multiple names have the maximum win count, randomly select one as the champion
        if len(max_wins_indices) > 1:
            champion_index = random.choice(max_wins_indices)
        else:
            champion_index = max_wins_indices[0]

        if max_wins < win_counts[champion_index]:
            max_wins = win_counts[champion_index]
            #print(f"New max wins: {max_wins}")

        champion_counts[names[champion_index]] += 1

    def calculate_win_probability(champion_counts):
        total_counts = sum(champion_counts.values())
        win_probabilities = {name: count / total_counts for name, count in champion_counts.items()}
        return win_probabilities

    win_probabilities = calculate_win_probability(champion_counts)
    print("Win probabilities:", win_probabilities)
    print("Champion counts:", champion_counts)

    return win_probabilities

@app.route('/all_games', methods=['GET'])
def get_all_games():
    games = fetch_games()
    in_progress_games = [game_to_json(game) for game in games if True]
    return jsonify(in_progress_games)

@app.route('/games', methods=['GET'])
def get_games():
    games = fetch_games()
    print
    in_progress_games = [game_to_json(game) for game in games if game.status == 'In Progress' or game.status == 'Halftime' or game.status == 'End of Period']
    return jsonify(in_progress_games)

# Endpoint to get the leaderboard
@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    games = fetch_games()
    games_dict = {game.bowl_name: game for game in games}
    all_picks = load_all_picks(games)
    
    # Analyze picks
    for picks in all_picks.values():
        picks.analyze_picks(games_dict)

    # Calculate scores and sort leaderboard
    # Perform simulations to calculate win probabilities
    win_probabilities = simulate_win_probabilities(all_picks, games_dict)
    leaderboard = []
    projected_totals = []  # List to store projected_totals
    for name, picks in all_picks.items():
        correct_picks = sum(1 for pick in picks.picks if pick.correct)
        projected_points = 0
        for pick in picks.picks:
            if pick.correct is None and pick.team is not None:  # Game has not been played yet
                game = pick.game
                win_percentage = calculate_winner_percentage(game)
                if win_percentage is not None:
                    if pick.team == game.projected_winner:
                        projected_points += win_percentage / 100
                    elif pick.team is not None:
                        projected_points += (1 - (win_percentage / 100))
                    else:
                        projected_points += 0
        total_projected = correct_picks + projected_points
        projected_totals.append(total_projected)  # Add projected_total to the list
        streak = picks.calculate_streak()  # Calculate the streak
        leaderboard.append({
            'name': name,
            'correct_picks': correct_picks,
            'streak': streak,
            'projected_total': total_projected
        })
    leaderboard.sort(key=lambda x: x['correct_picks'], reverse=True)

    mean = np.mean(projected_totals)  # Calculate the mean
    stdev = np.std(projected_totals)  # Calculate the standard deviation

    #print(f"Mean: {mean}, Standard Deviation: {stdev}")  # Debug print
    
    def convert_to_odds(probability):
        probability = probability / 100
        if probability == 0:
            return "N/A"
        if probability >= 0.5:
            # Favorite (probability >= 50%)
            odds = -100 * (probability / (1 - probability))
        else:
            # Underdog (probability < 50%)
            odds = 100 * ((1 - probability) / probability)

        return round(odds)

    # Update leaderboard with win probabilities
    for entry in leaderboard:
        entry['win_probability'] = win_probabilities[entry['name']] * 100  # Convert to percentage
        entry['odds_to_win'] = convert_to_odds(entry['win_probability'])
        #print(f"{entry['name']}: {entry['projected_total']}, {entry['win_probability']}, {entry['odds_to_win']}")

    return jsonify(leaderboard)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/picks/<name>', methods=['GET'])
def get_picks(name):
    print(f"Fetching picks for: {name}")  # Debug print
    file_name = f"{name.replace(' ', '_')}_picks.csv"
    file_path = os.path.join('picks', file_name)
    print(f"Looking for file: {file_path}")  # Debug print

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")  # Debug print
        return jsonify({'error': 'Picks not found'}), 404

    picks_data = read_picks_from_csv(file_path)
    games = fetch_games()
    games_dict = {game.bowl_name: game for game in games}

    # Create a Picks object and analyze the picks
    picks = Picks(name, picks_data, games)
    picks.analyze_picks(games_dict)

    # Serialize the picks to JSON
    picks_json = []
    for pick in picks.picks:
        if pick.team is None:
            team_data = {
                'display_name': 'No Pick',
                'short_display_name': 'No Pick',
                'location': 'No Pick',
                'abbreviation': 'No Pick',
            }
        else:
            team_data = {
                'display_name': pick.team.display_name,
                'short_display_name': pick.team.short_display_name,
                'location': pick.team.location,
                'abbreviation': pick.team.abbreviation,
            }
        pick_data = {
            'game': game_to_json(pick.game),
            'team': team_data,
            'correct': pick.correct
        }
        picks_json.append(pick_data)

    return jsonify(picks_json)

@app.route('/upcoming_games', methods=['GET'])
def get_upcoming_games():
    games = fetch_games()
    upcoming_games = [game for game in games if game.status == 'Scheduled'][:9]  # Select the next 7 games
    # You'll need to add logic to calculate the number of picks for each team
    # and the projected winner percentage based on the odds.
    # This is just a placeholder for the structure.


    upcoming_games_info = [
        {
            'bowl_name': game.bowl_name,
            'date': game.date.strftime('%Y-%m-%d %H:%M'),  # Format date as needed
            'home_team': game.home_team.location,
            'away_team': game.away_team.location,
            'projected_winner': game.projected_winner.location if game.projected_winner else None,
            'projected_winner_line': game.spread,  # Implement this function
            'home_team_picks': count_picks_for_team(game.home_team, games),  # Implement this function
            'away_team_picks': count_picks_for_team(game.away_team, games),  # Implement this function
        }
        for game in upcoming_games
    ]
    return jsonify(upcoming_games_info)

if __name__ == '__main__':
    app.run(debug=True)