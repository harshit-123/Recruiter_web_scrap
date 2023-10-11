import cloudscraper
import contextlib
from bs4 import BeautifulSoup
from datetime import datetime
import mysql.connector

url_list = []
BASE_URL = 'https://uk.indeed.com'
total_data_insert_count = 0
SITE = 'Indeed'

# DB Confiuration
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="cv-library"
)
mycursor = mydb.cursor()

def date_formated_timestamp():
    """
    This function get the current datetime 
    """
    now = datetime.now()
    year = now.year
    month = "{:02d}".format(now.month)
    day = "{:02d}".format(now.day)
    hour = "{:02d}".format(now.hour)
    minute = "{:02d}".format(now.minute)
    second = "{:02d}".format(now.second)
    return f"{year}-{month}-{day} {hour}:{minute}:{second}"


def insert_values_into_db(*args):
    try:
        print(f"SELECT * FROM indeed_jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%' AND posted_date = {args[1]}")
        mycursor.execute(f"SELECT * FROM indeed_jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%' AND posted_date = '{args[1]}'")
        # fetch all rows returned by the SELECT statement
        result = mycursor.fetchall()
        if len(result) == 0:
            global total_data_insert_count
            total_data_insert_count += 1
            sql = "INSERT INTO indeed_jobs (job_title, posted_date, location, url, site, created_at, updated_at, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (args[0], args[1], args[2], args[3], SITE, args[5], args[5], str(args[6]))
            mycursor.execute(sql, val)
            mydb.commit()
            # print(mycursor.rowcount, "record inserted.")
            print(total_data_insert_count, "record inserted.")
        else:
            print("Record Already Exist!")
    except Exception as e:
        print("ERROR: ", e)

scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
scrape = scraper.get("https://uk.indeed.com/jobs?q=&l=United+Kingdom&fromage=1&vjk=7735c9541c95ecde")
soup = BeautifulSoup(scrape.text, 'lxml')
get_ol = soup.find('ul', attrs={'class': 'jobsearch-ResultsList'})
get_jobs = get_ol.find_all('h2', class_='jobTitle')

for title in get_jobs:
    href_page = title.find('a')['href']
    # Get the href attribute value
    print(f"{BASE_URL}{href_page}")
    url_list.append(f"{BASE_URL}{href_page}")
# print(len(url_list))

for url in url_list:
    try:
        scraper_inside = cloudscraper.create_scraper()
        scrape = scraper_inside.get(f"{url}")
        soup = BeautifulSoup(scrape.text, 'lxml')
        current_date = date_formated_timestamp()
        posted_formated_date = current_date
        main_div = soup.find('div', class_ ='jobsearch-ViewJobLayout-jobDisplay')
        job_title = main_div.find('h1').text.strip()
        print(job_title)
        description = soup.find('div', attrs={'id': 'jobDescriptionText'})
        location = soup.find('div', class_='css-6z8o9s').text
        # insert_values_into_db(job_title, posted_formated_date, location, url, SITE, current_date, description)
    except Exception as e:
        print(e)