import json

# Assuming you have the JSON data in a variable called 'data'
with open('data.json') as file:
    data = json.load(file)

formatted_json = json.dumps(data, indent=4)

# This will save the formatted JSON data
with open('formatted_data.json', 'w') as file:
    file.write(formatted_json)
