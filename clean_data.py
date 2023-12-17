import os
import pandas as pd

# Load the provided Excel file
file_path = 'picks/2023 Bowl Picks Start 2.xlsx'
df = pd.read_excel(file_path)

# Display the first few rows of the dataframe to understand its structure
df.head()


# Create a directory for the picks
picks_dir = 'picks2'
os.makedirs(picks_dir, exist_ok=True)

# Extract the first row as header
header = df.iloc[0]
# Update the dataframe to exclude the first row and set the correct header
df.columns = header
df = df[1:]

# List of files created
created_files = []

# Iterate over each column (excluding the first one which is the Bowl name)
for column in df.columns[1:]:
    # Skip empty columns
    if column is None or pd.isna(column) or column == 'Matchup' or column == 'Date' or column == "Time (ET)":
        continue
    
    # Split the name into first and last name and create the file name
    file_name = f"{column.replace(' ','_').strip()}_picks.csv"

    # Create a dataframe for each person's picks
    picks_df = pd.DataFrame({
        'game': df['Bowl'],
        'team': df[column]
    })

    # Save the dataframe as a CSV file
    full_file_path = os.path.join(picks_dir, file_name)
    picks_df.to_csv(full_file_path, index=False)
    created_files.append(full_file_path)



