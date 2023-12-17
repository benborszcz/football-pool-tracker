import requests
import time

# Function to format the event information
def format_event(event):
    # Get the name of the bowl (if available)
    bowl_name = event.get('competitions', [{}])[0].get('notes', [{}])[0].get('headline', 'Unknown Bowl')

    # Get the competitors and their scores
    competitors = event.get('competitions', [{}])[0].get('competitors', [])
    team_info = []
    for team in competitors:
        team_name = team.get('team', {}).get('location', 'Unknown Team')
        score = team.get('score', '0')
        team_info.append(f"{team_name} {score}")

    # Get the game status
    status = event.get('status', {})
    display_clock = status.get('displayClock', '00:00')
    period = status.get('period', 0)
    period_name = 'OT' if period > 4 else f"{period}"
    time_status = f"{display_clock} - {period_name}"

    # Get the current situation
    situation = event.get('competitions', [{}])[0].get('situation', {})
    down_distance_text = situation.get('downDistanceText', '')
    possession_text = situation.get('possessionText', '')

    # Get the betting odds (if available)
    odds_info = event.get('competitions', [{}])[0].get('odds', [{}])[0]
    odds_details = odds_info.get('details', 'No odds available')
    over_under = odds_info.get('overUnder', None)
    spread = odds_info.get('spread', None)

    # Format the odds information
    if over_under and spread:
        formatted_odds = f"Odds: {odds_details}, Over/Under: {over_under}, Spread: {spread}"
    else:
        formatted_odds = "Odds: Not available"

    # Format the output
    formatted_event = f"{bowl_name}\n" \
                      f"{' vs '.join(team_info)}\n" \
                      f"{time_status}\n" \
                      f"{down_distance_text}, {possession_text}\n" \
                      f"{formatted_odds}\n"

    return formatted_event

# Function to fetch and display events
def fetch_and_display_events():
    url = 'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard'
    response = requests.get(url)
    data = response.json()

    # Iterate over all events and print the formatted information
    for event in data.get('events', []):
        print(format_event(event))
        print('-' * 40)  # Separator between events

# Set an interval for how often you want to update the information (in seconds)
update_interval = 60*5

# Main loop to fetch and display events every 'update_interval' seconds
try:
    while True:
        fetch_and_display_events()
        time.sleep(update_interval)
except KeyboardInterrupt:
    print("Stopped updating events.")