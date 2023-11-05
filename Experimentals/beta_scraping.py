import requests
from bs4 import BeautifulSoup
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_individual_course_data(course_code):
    url = f'https://www.bu.edu/academics/cds/courses/{course_code.lower().replace(" ", "-")}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract credits
    credits_tag = soup.find('dt', string='Credits:')
    credits = credits_tag.find_next('dd').text.strip() if credits_tag and credits_tag.find_next('dd') else None
    
    # Initialize schedule data structure with two keys for each term
    schedule_data = {
        "FALL 2023": [],
        "SPRG 2024": []
    }
    
    # Find all headers that contain "FALL 2023" or "SPRG 2024"
    headers = soup.find_all('h4')
    for header in headers:
        term = None
        if 'FALL 2023' in header.text:
            term = 'FALL 2023'
        elif 'SPRG 2024' in header.text:
            term = 'SPRG 2024'
        
        if term:
            # Find the table immediately following the header
            schedule_table = header.find_next_sibling('table')
            if schedule_table:
                header_cells = schedule_table.find('tr').find_all('th')
                # Exclude the "Notes" column
                headers = [th.get_text(strip=True) for th in header_cells if "Notes" not in th.get_text(strip=True)]
                rows = schedule_table.find_all('tr')[1:]  # Exclude header row
                for row in rows:
                    cells = row.find_all('td')[:-1]  # Exclude the "Notes" cell
                    if len(cells) == len(headers):  # Match the number of headers
                        section_info = {headers[i]: cell.get_text(strip=True) for i, cell in enumerate(cells)}
                        schedule_data[term].append(section_info)
    
    return credits, schedule_data



# ... rest of your code

# Please replace your existing get_individual_course_data function with this updated version and run your script again.



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
                
                # Fetch additional data from the individual course page
                credits, schedule_data = get_individual_course_data(course_code)
                course_data['Credits'] = credits
                course_data['Schedule'] = schedule_data
                
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

base_url = 'https://www.bu.edu/academics/cds/courses/{}/'

def get_all_course_data():
    course_info_list = []
    for page_number in range(1, 5):
        target_url = base_url.format(page_number)
        try:
            courses = get_course_data(target_url)
            course_info_list.extend(courses)
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
    return course_info_list

try:
    courses = get_all_course_data()
    with open('Courses.json', 'w') as f:
        json.dump(courses, f, indent=4)
except requests.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")

# Load the data from the file
with open('Courses.json', 'r') as f:
    data = json.load(f)

# Filter out the unwanted entries, clean the description field
new_data = [
    {key: value for key, value in dict(
        item, description=re.sub(' +', ' ', item['description'].replace('\n', ' ').replace('\t', ' ')) if 'description' in item else None
    ).items()}
    for item in data if "course_code" in item
]

# Save the cleaned data to a new file
with open('TEST-CDS-Courses.json', 'w') as f:
    json.dump(new_data, f, indent=4)