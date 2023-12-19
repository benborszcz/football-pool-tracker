# Football Pool Tracker

Welcome to the Football Pool Tracker, a web application designed to help you manage and track picks for your football pool. This application provides real-time updates on football games, a leaderboard to see who's ahead, and detailed pick information for each participant.

## Features

- **Real-time Game Updates**: Stay informed with live updates on ongoing football games, including scores, win probabilities, and game status.
- **Leaderboard**: Check out the current standings with the leaderboard, which displays correct picks, winning streaks, and each participant's chance to win the pool.
- **Participant Picks**: View detailed pick information for each participant, including their selections for upcoming games and the outcomes of past games.
- **Upcoming Games**: Get a preview of upcoming games, including team matchups, game times, and the number of picks for each team.

## Installation

To run the Football Pool Tracker, you'll need to have Python and the necessary libraries installed. You can also run the application using Docker.

### Running Locally

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required Python libraries:
   ```
   pip install Flask pandas requests numpy
   ```
4. Run the application:
   ```
   python app.py
   ```

### Running with Docker

1. Ensure you have Docker installed on your system.
2. Build the Docker image:
   ```
   docker build -t football-pool-tracker .
   ```
3. Run the Docker container:
   ```
   docker run -p 5000:5000 football-pool-tracker
   ```

## Usage

Once the application is running, you can access it by visiting `http://localhost:5000` in your web browser.

- **Viewing Live Games**: The homepage displays live updates on ongoing games.
- **Checking the Leaderboard**: Click on the "Leaderboard" tab to see the current standings.
- **Viewing Participant Picks**: Click on a participant's name in the leaderboard to view their picks.
- **Previewing Upcoming Games**: The "Upcoming Games" section shows the next games scheduled, along with pick counts and projected winners.

## Pick Format and Abbreviations

To ensure the Football Pool Tracker functions correctly, it is important that the picks are provided in the correct format and that team abbreviations match those used by ESPN.

### Pick Format

Picks should be submitted in a CSV file with the following columns:

- `game`: The name of the bowl or game.
- `team`: The abbreviation of the team picked to win.

Each participant's picks should be in a separate CSV file named in the format `{participant_name}_picks.csv`. The `clean_data.py` script is provided to help convert an Excel file into the required CSV format.

### Team Abbreviations

The team abbreviations used in the picks must exactly match those provided by ESPN. This is crucial for the application to correctly identify the teams and update the game outcomes. If there is a mismatch in abbreviations, the application may not be able to process the picks correctly.

## Contributing

Contributions to the Football Pool Tracker are welcome! If you have suggestions for improvements or new features, feel free to create an issue or submit a pull request.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Contact

For any questions or comments, please open an issue in the repository, and we'll get back to you as soon as possible.

Enjoy tracking your football pool with the Football Pool Tracker! 🏈