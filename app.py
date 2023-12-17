from flask import Flask, jsonify
import csv
import os
from data_retrieval import fetch_games, Team, Game
from picks import Picks  


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
    picks_folder = 'picks2'
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
        'winner': game.winner.abbreviation if game.winner else None,
    }

@app.route('/all_games', methods=['GET'])
def get_all_games():
    games = fetch_games()
    in_progress_games = [game_to_json(game) for game in games if True]
    return jsonify(in_progress_games)

@app.route('/games', methods=['GET'])
def get_games():
    games = fetch_games()
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
    leaderboard = []
    for name, picks in all_picks.items():
        correct_picks = sum(1 for pick in picks.picks if pick.correct)
        leaderboard.append({'name': name, 'correct_picks': correct_picks})
    leaderboard.sort(key=lambda x: x['correct_picks'], reverse=True)

    return jsonify(leaderboard)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/picks/<name>', methods=['GET'])
def get_picks(name):
    print(f"Fetching picks for: {name}")  # Debug print
    file_name = f"{name.replace(' ', '_')}_picks.csv"
    file_path = os.path.join('picks2', file_name)
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

if __name__ == '__main__':
    app.run(debug=True)