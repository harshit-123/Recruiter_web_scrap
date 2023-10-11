import requests
from bs4 import BeautifulSoup
import datetime
import time 
#import schedule
import mysql.connector

# DB Confiuration
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dbMysql@123a",
    database="recruiter"
)
mycursor = mydb.cursor()

BASE_URL = 'CV Library'
LINK = 'https://www.cv-library.co.uk'
total_data_insert_count = 0
latest_job_id = 0
unique_job_no = 0
flag_to_break_loop = False
page_links = []

def date_formated():
    """
    This function get the current datetime 
    """
    now = datetime.datetime.now()
    year = now.year
    month = "{:02d}".format(now.month)
    day = "{:02d}".format(now.day)
    hour = "{:02d}".format(now.hour)
    minute = "{:02d}".format(now.minute)
    second = "{:02d}".format(now.second)
    return f"{year}-{month}-{day} {hour}:{minute}:{second}"


def hit_url_with_id(inserted_record_id):
    print("XXXXXX", inserted_record_id)
    print(type(inserted_record_id))
    url = f"http://127.0.0.1:8000/api/get_id/{inserted_record_id}"
    data = {"id": inserted_record_id}
    response = requests.post(url, data)

def insert_values_into_db(*args):
    try:
        # print("args==>", args[7])
        # print("inside db record func") 
        mycursor.execute(f"SELECT * FROM jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%'")
        # fetch all rows returned by the SELECT statement
        result = mycursor.fetchall()
        # print("result==>", result)
        if not result:
            global total_data_insert_count
            total_data_insert_count += 1
            sql = "INSERT INTO jobs (job_title, posted_date, location, url, site, created_at, updated_at, description, unique_job_no, not_found) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (args[0], args[1], args[2], args[3], BASE_URL, args[1], args[1], str(args[5]), args[6], args[7])
            mycursor.execute(sql, val)
            mydb.commit()
            inserted_record_id = mycursor.lastrowid
            print("Inserted Record ID:", inserted_record_id)
            hit_url_with_id(inserted_record_id)
            print(total_data_insert_count, "record inserted.")
        else:
            pass
            # print("Record Already Exist!")
    except Exception as e:
        pass
        # print("ERROR: ", e)


def get_latest_job_from_previous_day():
    try:
        global latest_job_id
        mycursor.execute(f"SELECT Max(unique_job_no) AS latest_job_id FROM jobs WHERE site = '{BASE_URL}'")
        result = mycursor.fetchone()
        # print("result==>", result)
        # Check if there is a result and print it
        if result[0] != None:
            latest_job_id = result[0]
            # print("Latest Job ID:", latest_job_id)
            return latest_job_id
        else:
            # print("No result found.")
            return 0
        # mydb.commit()
    except Exception as e:
        pass
        # print("ERROR: ", e)

latest_job_id= get_latest_job_from_previous_day()
# print("latest_job_id123===>", latest_job_id)
def extract_page():
    global last_page
    global flag_to_break_loop
    html_text = requests.get(
        "https://www.cv-library.co.uk/jobs?order=date&posted=1"
    ).text
    soup = BeautifulSoup(html_text, 'lxml')
    get_ol = soup.find('ol', class_='results')
    get_all_lis = get_ol.select("li.results__item, li.results__item.featured-jobs.search-card")
    for li in get_all_lis:
        href = li.find('a')['href']
        link = f"{LINK}{href}"
        page_links.append(link)


        break
i = 0
link = ''
html_text = ''
unique_job_no = 0
while flag_to_break_loop != True:
    if i == 0:
        extract_page()
        link = page_links[0]
    import contextlib
    with contextlib.suppress(Exception):
        unique_job_no = link.split('/')[4] if i == 0 else unique_job_no
        # print("latest_job_id==>", latest_job_id)
        # print("unique_job_no==>", unique_job_no)
        if latest_job_id == 0:
            # print("if unique_job_no===>", unique_job_no)
            latest_job_id = unique_job_no
            html_text = requests.get(link).text
            # print("link if==>", link)
        else:
            latest_job_id = int(latest_job_id) + 1
            # print("latest_job_id by 1==>", latest_job_id)
            get_link = f"https://www.cv-library.co.uk/job/{latest_job_id}/"
            # get_link = new_link
            # print("link else===>", get_link)
            # print("latest_job_id else===>", latest_job_id)
            html_text = requests.get(get_link).text
        soup = BeautifulSoup(html_text, 'lxml')
        title = soup.find('title').text
        # print("title==>", title)
        

        position = soup.find('section', attrs={'id': 'expired'})
        if position:
            position = soup.find('section', attrs={'id': 'expired'}).find('p').text
            # print("position==>", position)
        
            if 'The position you are looking for' in position:
                # print("inside pos")
                continue
        # print("title==>", title)
        if 'Page NOT Found' in title:
            # print("break loop")
            heading = "NULL"
            current_datetime = "NULL"
            location = "NULL"
            link = "NULL"
            BASE_URL = BASE_URL
            description = "NULL"
            # latest_job_id = "NULL"
            # insert_values_into_db(heading, current_datetime, location, link, BASE_URL, description, latest_job_id, not_found)
            sql = "INSERT INTO jobs (job_title, posted_date, location, url, site, created_at, updated_at, description, unique_job_no, not_found) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (heading, current_datetime, location, link, BASE_URL, description, latest_job_id, "NULL", latest_job_id, 1)
            mycursor.execute(sql, val)
            mydb.commit()
            # print(total_data_insert_count, "record inserted.")
            flag_to_break_loop = True
        heading = soup.find('h1', class_='job__title')
        if heading is None:
            heading = soup.find_all('dd', attrs={'class': 'job__details-value'})[0].text.strip()
            location = soup.find_all('dd', attrs={'class': 'job__details-value'})[2].text.strip()
            description = soup.find('div', attrs={'class': 'premium-description'})

        else:
            heading = soup.find('h1', class_='job__title').text.strip()
            location = soup.find('dd', attrs={'class': 'job__details-value'}).text.strip()
            description = soup.find('div', attrs={'class': 'job__description'})
        current_datetime = date_formated()
        link = link if latest_job_id == 0 else get_link
        i += 1
        # print("=======")
        not_found = 0
        insert_values_into_db(heading, current_datetime, location, link, BASE_URL, description, latest_job_id, not_found)
        unique_job_no = int(unique_job_no) + 1