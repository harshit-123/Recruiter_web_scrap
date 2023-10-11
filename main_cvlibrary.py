import contextlib
import requests
from bs4 import BeautifulSoup
import datetime
import mysql.connector
from concurrent.futures import ProcessPoolExecutor


# DB Confiuration
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="jobs"
)
mycursor = mydb.cursor()

BASE_URL = 'CV Library'
LINK = 'https://www.cv-library.co.uk'
total_data_insert_count = 0
page_links_12 = []

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


def insert_values_into_db(*args):
    with contextlib.suppress(Exception):
        mycursor.execute(f"SELECT * FROM jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%'")
        # fetch all rows returned by the SELECT statement
        result = mycursor.fetchall()
        if len(result) == 0:
            global total_data_insert_count
            total_data_insert_count += 1
            sql = "INSERT INTO jobs (job_title, posted_date, location, url, site, created_at, updated_at, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (args[0], args[1], args[2], args[3], BASE_URL, args[1], args[1], str(args[5]))
            mycursor.execute(sql, val)
            mydb.commit()
            print("record inserted.")
        else:
            print("Record Already Exist!")
        # print("ERROR: ", e)

        
def extract_page(page_num):
    print("Page_num==>", page_num)
    # html_text = requests.get(f"https://www.cv-library.co.uk/jobs?page={page_num}&posted=1&us=1").text
    html_text = requests.get(f"https://www.cv-library.co.uk/jobs?order=date&page={page_num}&posted=1").text
    soup = BeautifulSoup(html_text, 'lxml')
    get_ol = soup.find(id='searchResults')
    all_jobs = get_ol.find_all(class_='results__item')
    for li in all_jobs:
        if "featured-jobs" in li["class"]:
            print("FJ")
            continue
        else:
            href = li.find('a')['href']
            link = f"{LINK}{href}"
            # print(link)
            page_links_12.append(link)
        return page_links_12
print("All data Inserted!")


def extract(link):
    with contextlib.suppress(Exception):
        html_text = requests.get(link).text
        soup = BeautifulSoup(html_text, 'lxml')
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
            insert_values_into_db(heading, current_datetime, location, link, BASE_URL, description)
    page_num += 1


if __name__ == "__main__":
    print("Main Run")
    # with ProcessPoolExecutor() as executor:
    page_links = list(map(extract_page, list(range(1,41))))
        # print(page_links_12)
    with ProcessPoolExecutor() as executor:
        executor.map(extract, page_links)
    print(total_data_insert_count, "record inserted.")