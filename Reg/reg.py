import requests
import re
from selenium.webdriver.common.by import By
from selenium import webdriver

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import time

TURN_ON_REAL_REGISTRATION = True

#set the module as the planner
module = 'reg/plan/add_planner.pl'
is_planner = 'Y'

if TURN_ON_REAL_REGISTRATION:
    #set the module for real class registration
    module = 'reg/add/confirm_classes.pl'
    is_planner = ''
    
    
'''
Press F12 in chrome, navigate to the Network tab, then go to your planner on student link, 
click on the item with a long number, under request headers find "Cookie: .... "
Copy the `cookie` header below
'''
cookies = 'f5avraaaaaaaaaaaaaaaa_session_=OBAADKKMDFCDJLGGHPAKLIHECHPMNIIJLDCNHALHJJNOGEAPFCEDGDDGIIDFBHGFPOPDAIEEFDJCOJDIPMOAFDIHELAOLACDBPKIPFPIPMHFAHBEOFJEINKBFOHHGNNG; apt.uid=AP-PQQY5YJEHTTA-2-1687898055794-89777277.0.2.ce8d9ea4-685b-48eb-8ce0-69091b7b0a10; __utma=21468840.1058874054.1687898063.1687970472.1687970472.1; __utmz=21468840.1687970472.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _ga_0Z1EBE5RV7=GS1.1.1687970472.1.1.1687970770.0.0.0; _ga=GA1.1.1058874054.1687898063; _ga_L4SD8HKLDR=GS1.1.1694293664.5.1.1694293689.0.0.0; BIGipServerist-uiscgi-app-prod-443-pool=1254475136.47873.0000; uiscgi_prod=fc4403bbe7570112c4a1e52d4cde5201:prod; BIGipServerist-uiscgi-content-prod-443-pool=2315708170.47873.0000; f5avr0778797390aaaaaaaaaaaaaaaa_cspm_=CNNIENIOJJFGLNFLIEPBIOPHNMJKBNBKFCIOIOCOFODBJNECGPNPECKINNFLKAOIOBECOFNJBHPDAEOFEOEAMJHDAINDPPNGCOAILMFOIPLBMPFACBOGALLENKOILMLL; _ga_F7T3KG2073=GS1.1.1698608012.1.1.1698608120.0.0.0'


#You might also have to copy the other headers into here
def generate_headers():
    return {'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': cookies,
    'DNT': '1',
    'Host': 'www.bu.edu',
    'Referer': 'https://www.bu.edu/link/bin/uiscgi_studentlink.pl/1524338857/1524338857',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
    }



url = 'https://www.bu.edu/link/bin/uiscgi_studentlink.pl/1524289373'

def generate_params(college, dept, course, section):
    return {
    'College': college,
    'Dept': dept,
    'Course': course,
    'Section': section,
    'ModuleName': 'reg/add/browse_schedule.pl',
    'AddPreregInd': '',
    'AddPlannerInd': '',
    'ViewSem': 'Spring 2024',
    'KeySem': '',
    'PreregViewSem':  '',
    'PreregKeySem':  '',
    'SearchOptionCd': 'S',
    'SearchOptionDesc': 'Class Number',
    'MainCampusInd': '',
    'BrowseContinueInd': '', 
    'ShoppingCartInd': '' ,
    'ShoppingCartList': '' }

def generate_reg_params(college, dept, course, section, ssid):
    return {'SelectIt': ssid, 
    'College':college.upper(),
    'Dept':dept.upper(),
    'Course':course, 
    'Section':section.upper(),
    'ModuleName': module,
    'AddPreregInd': '',
    'AddPlannerInd': is_planner,
    'ViewSem':'Spring 2024',
    'KeySem':'',
    'PreregViewSem':'',
    'PreregKeySem':'',
    'SearchOptionCd':'S',
    'SearchOptionDesc':'Class Number',
    'MainCampusInd':'',
    'BrowseContinueInd':'',
    'ShoppingCartInd':'',
    'ShoppingCartList':''}
    
# Replace with your own BU login and password.
# Your credentials are only stored in this file, and I am not liable if you expose this file to anyone else.
def credentials():
    return ('xfu@bu.edu', 'gC1DFlR0hYdS')

def login():
    print('logging in...')
    # Here we are using Firefox instead of Chrome
    driver = webdriver.Firefox()

    driver.get("https://www.bu.edu/link/bin/uiscgi_studentlink.pl/1524541319?ModuleName=regsched.pl")
    username, password = credentials()
    driver.find_element("id", 'j_username').send_keys(username)
    driver.find_element("id", 'j_password').send_keys(password)
    driver.find_element("class name", 'input-submit').click()

    while 'studentlink' not in driver.current_url:
        time.sleep(3)
        
    # Retrieve cookies and update the global variable
    cookies_list = driver.get_cookies()
    global cookies
    cookies = ''
    for cookie in cookies_list:
        cookies = cookies + cookie['name'] + '=' + cookie['value'] + '; '
    print('Retrieving cookies: ' + cookies)
    driver.close()


'''
Finds course listing and tries to register for the class.

Sometimes course names are wrong, use at your own discretion. 
'''
def find_course(college, dept, course, section):
    name =  dept.upper() + course + ' ' + section.upper()
    print('searching for ' + name)
    params_browse = generate_params(college, dept, course, section)
    headers = generate_headers()
    ####
    for retry in range(1, 5):
        #logging.warning('[fetch] try=%d, url=%s' % (retry, url))
        retry_because_of_timeout = False
        try:
            r = requests.get(url, headers=headers,params=params_browse, timeout = 3)
            text = r.text
        except Exception as e:
            retry_because_of_timeout=True
            pass
    
        if retry_because_of_timeout:
            time.sleep(retry * 2 + 1)
        else:
            break
    ####
    #print(r.text)
    #(?<=abc)
    p = re.compile('<tr ALIGN=center Valign= top>.+?</td></tr>', re.DOTALL)
    m = p.findall(text)
    if len(m) == 0:
        print('Something went wrong with the request for ' + dept + course)
        login()
        find_course(college, dept, course, section)
        return
    s = college.upper() + dept.upper() + course + '%20' + section.upper()

    found = False
    for item in m:
        if re.search(s, item):
            found = True
            n = re.search('value="(\d{10})"', item)
            if n:
                params_reg = generate_reg_params(college, dept, course, section, n.group(1))
                reg = requests.get(url, headers=headers,params=params_reg)
                o = re.search('<title>Error</title>', reg.text)
                if o:
                    print('Can not register yet :/')
                else:
                    print('Registered successfully!')
            else:
                print('Class is full :(')
            break
    if not found:
        print('could not find course')

# Replace with your own course.
# Ex. ('cas','wr','100','a1')
my_courses = [
    ('CDS', 'DS', '320', 'A1'),  # First course
    ('CAS', 'MA', '684', 'A1'),  # Second course
    ('ENG', 'EC', '414', 'A1'),  # Third course
    # Add more courses as needed
]


beginning = time.time()
cycles = 0
login()
while True:
    for i in my_courses:
        print('\n['+str(time.asctime())+']')
        start = time.time()
        find_course(*i)
        duration = (time.time() - start)
        print('Took ' + str(round(duration, 1)) + ' seconds')
        cycles+=1
        print('Average time: ' + str(round((time.time() - beginning)/cycles,1)))


    
