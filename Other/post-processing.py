import json
import re

# Load the data from the file
with open('updated_courses.json', 'r') as f:
    data = json.load(f)

# Filter out the unwanted entries and clean the description field
new_data = [
    dict(item, description=re.sub(' +', ' ', item['description'].replace('\n', ' ').replace('\t', ' ')))
    for item in data if "course_code" in item
]

# Save the cleaned data to a new file
with open('cleaned_data.json', 'w') as f:
    json.dump(new_data, f, indent=4)
