import json
import pandas as pd

# Read the CSV and convert to JSON
df = pd.read_csv('data.csv', low_memory=False)
df.to_json('output.json', orient='records')

# Read the JSON file, format it, and overwrite the file
with open('output.json', 'r') as file:
    data = json.load(file)

with open('processed.json', 'w') as file:
    json.dump(data, file, indent=4)