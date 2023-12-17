import requests
import pandas as pd
import tkinter as tk
from tkinter import ttk

# Function to fetch events and return as a Pandas DataFrame
def fetch_events_dataframe():
    url = 'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard'
    response = requests.get(url)
    data = response.json()
    events = data.get('events', [])

    # Create a list to hold all event data
    events_data = []

    for event in events:
        # Extract event information as before
        bowl_name = event.get('competitions', [{}])[0].get('notes', [{}])[0].get('headline', 'Unknown Bowl')
        competitors = event.get('competitions', [{}])[0].get('competitors', [])
        
        # Initialize variables for home and away teams
        home_team = away_team = home_score = away_score = 'TBD'
        
        # Loop through the competitors to assign home and away teams
        for team in competitors:
            if team.get('homeAway') == 'home':
                home_team = team.get('team', {}).get('location', 'Unknown Team')
                home_score = team.get('score', '0')
            elif team.get('homeAway') == 'away':
                away_team = team.get('team', {}).get('location', 'Unknown Team')
                away_score = team.get('score', '0')

        status = event.get('status', {})
        display_clock = status.get('displayClock', '00:00')
        period = status.get('period', 0)
        period_name = 'OT' if period > 4 else f"{period}th"
        time_status = f"{display_clock} - {period_name}"
        status_type = status.get('type', {})
        game_completed = status_type.get('completed', False)
        
        # Check if the game is completed and set down and distance text accordingly
        if game_completed:
            time_status = "FINAL"
            # Determine the winner
            winner = None
            if home_score > away_score:
                winner = home_team
            elif away_score > home_score:
                winner = away_team
            
            # Add the winner to the down and distance text
            down_distance_text = f"{winner} Wins!" if winner else "Game Tied"
        else:
            situation = event.get('competitions', [{}])[0].get('situation', {})
            down_distance_text = situation.get('downDistanceText', '')
            possession_text = situation.get('possessionText', '')
            down_distance_text = f"{down_distance_text}"
        
        odds_info = event.get('competitions', [{}])[0].get('odds', [{}])[0]
        odds_details = odds_info.get('details', 'N/A')
        over_under = odds_info.get('overUnder', None)
        spread = odds_info.get('spread', None)

        # Append a dictionary of the event data to the list
        events_data.append({
            'Bowl': bowl_name,
            'H Team': home_team,
            'H Score': home_score,
            'A Team': away_team,
            'A Score': away_score,
            'Time': time_status,
            'Down': f"{down_distance_text}",
            'Odds': odds_details,
            'O/U': over_under,
            'Spread': spread
        })

    # Convert the list of event data into a Pandas DataFrame
    df = pd.DataFrame(events_data)
    return df

# Function to create and update the GUI
def create_gui():
    # Fetch the initial DataFrame
    df = fetch_events_dataframe()

    # Create the main window
    root = tk.Tk()
    root.title("College Football Scores and Odds")

    # Create a Treeview to display the DataFrame
    tree = ttk.Treeview(root)
    tree.pack(expand=True, fill='both')

    # Define a function to update the Treeview with new data
    def update_treeview():
        # Fetch new data
        new_df = fetch_events_dataframe()

        # Clear the Treeview
        tree.delete(*tree.get_children())

        # Set up new Treeview columns
        tree['columns'] = list(new_df.columns)
        tree['show'] = 'headings'
        for col in new_df.columns:
            tree.heading(col, text=col)
            # Set the width of each column
            if col == 'Bowl':
                tree.column(col, width=200)
            elif col == 'H Score' or col == 'A Score' or col == 'O/U' or col == 'Spread' or col == 'Time':
                tree.column(col, width=50)
            elif col == 'Down':
                tree.column(col, width=175)
            elif col == 'Odds':
                tree.column(col, width=75)
            else:
                tree.column(col, width=100)  # Adjust the width as desired

        # Add data to the Treeview
        for _, row in new_df.iterrows():
            tree.insert('', 'end', values=list(row))

        # Schedule the next update
        root.after(60000*5, update_treeview)  # Update every 60 seconds

    # Initial population of the Treeview
    update_treeview()

    # Start the GUI loop
    root.mainloop()

# Run the GUI
create_gui()