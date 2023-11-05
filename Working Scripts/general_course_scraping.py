import requests
from bs4 import BeautifulSoup
import json
import re

def get_course_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    course_info_list = []
    courses = soup.find_all('li')
    
    for i, course in enumerate(courses, 1):
        title_element = course.find('a')
        if title_element and title_element.strong:
            course_data = {}
            course_code_title = title_element.strong.text.split(':')
            if len(course_code_title) == 2:
                course_code = course_code_title[0].strip()
                course_data['course_code'] = course_code
                course_data['course_title'] = course_code_title[1].strip()
                description_text = course.text.split('\n', 2)[-1].strip()
                if description_text:
                    course_data['description'] = description_text
                prerequisites = course.find(text=lambda x: 'Prerequisites:' in x)
                if prerequisites:
                    course_data['prerequisites'] = prerequisites.split(':', 1)[-1].strip()
                hub_areas = course.find('div', class_='cf-hub-ind')
                if hub_areas:
                    hub_list = hub_areas.find_all('li')
                    course_data['BU_Hub'] = [hub_area.text for hub_area in hub_list]
                course_info_list.append(course_data)
    return course_info_list

base_url = 'https://www.bu.edu/academics/wheelock/courses/{}/'

def get_all_course_data():
    course_info_list = []
    for page_number in range(1, 27):  # This will loop through 1, 2, 3, ..., 7
        # ... rest of your code
        target_url = base_url.format(page_number)
        try:
            courses = get_course_data(target_url)
            course_info_list.extend(courses)  # Extending the list with newly fetched course data
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
    return course_info_list


try:
    courses = get_all_course_data()
    with open('courses.json', 'w') as f:
        json.dump(courses, f, indent=4)
except requests.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")

# Load the data from the file
with open('courses.json', 'r') as f:
    data = json.load(f)

# Filter out the unwanted entries, clean the description field
new_data = [
    {key: value for key, value in dict(
        item, description=re.sub(' +', ' ', item['description'].replace('\n', ' ').replace('\t', ' ')) if 'description' in item else None
    ).items()}
    for item in data if "course_code" in item
]

# Save the cleaned data to a new file
with open('Wheelock-Courses.json', 'w') as f:
    json.dump(new_data, f, indent=4)
