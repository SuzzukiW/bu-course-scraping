import json
import os

def merge_json_files(file_paths, output_file_path):
    combined_data = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            data = json.load(f)
            combined_data.extend(data)  # Assumes the data is a list
    
    with open(output_file_path, 'w') as f:
        json.dump(combined_data, f, indent=4)

# List of file paths to merge
file_paths = [f for f in os.listdir('.') if f.endswith('-Courses.json')]

# Output file path
output_file_path = 'full_list.json'

# Call the function to merge the files
merge_json_files(file_paths, output_file_path)
