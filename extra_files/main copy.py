import requests
from bs4 import BeautifulSoup
import datetime
import time 
import schedule
import mysql.connector

# DB Confiuration
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="cv-library"
)
mycursor = mydb.cursor()


SITE = 'CV Library'
LINK = 'https://www.cv-library.co.uk'
last_page = True
page_num = 1
total_data_insert_count = 0

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
    try:
        mycursor.execute(f"SELECT * FROM jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%'")
        # fetch all rows returned by the SELECT statement
        result = mycursor.fetchall()
        if len(result) == 0:
            global total_data_insert_count
            total_data_insert_count += 1
            sql = "INSERT INTO jobs (job_title, posted_date, location, url, site, created_at, updated_at, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (args[0], args[1], args[2], args[3], SITE, args[1], args[1], str(args[5]))
            mycursor.execute(sql, val)
            mydb.commit()
            # print(mycursor.rowcount, "record inserted.")
            print(total_data_insert_count, "record inserted.")
        else:
            print("Record Already Exist!")
    except Exception as e:
        print("ERROR: ", e)

# def job():
print("Running Python file every night at 11 PM")
# global last_page
# global page_num
while last_page:
    html_text = requests.get(f"https://www.cv-library.co.uk/jobs?page={page_num}&posted=1&us=1").text
    soup = BeautifulSoup(html_text, 'lxml')
    get_ol = soup.find('ol', class_='results')
    get_all_lis = get_ol.select("li.results__item, li.results__item.featured-jobs.search-card")
    check_page_num = soup.find('nav', attrs={'class': 'pagination--center'})
    a_tag_page = check_page_num.find_all('a')
    # Get the href attribute value
    last_page_index = a_tag_page[-1]['href'].split('&')[0].split('=')[-1]
    print(f"page_num===> {page_num}, last_page_index====> {last_page_index}")
    page_links = []
    if page_num != int(last_page_index):
        for li in get_all_lis:
            if "featured-jobs" in li["class"]:
                continue
            # Get the href attribute value
            href = li.find('a')['href']
            link = f"{LINK}{href}"
            page_links.append(link)

        for link in page_links:
            try:
                html_text = requests.get(link).text
                soup = BeautifulSoup(html_text, 'lxml')
                heading = soup.find('h1', class_='job__title')
                if heading != None:
                    heading = soup.find('h1', class_='job__title').text.strip()
                    location = soup.find('dd', attrs={'class': 'job__details-value'}).text.strip()
                    description = soup.find('div', attrs={'class': 'job__description'})
                else:
                    div = soup.find('div', class_='card--grey mt10')
                    heading = soup.find_all('dd', attrs={'class': 'job__details-value'})[0].text.strip()
                    location = soup.find_all('dd', attrs={'class': 'job__details-value'})[2].text.strip()
                    description = soup.find('div', attrs={'class': 'premium-description'})

                current_datetime = date_formated()
                insert_values_into_db(heading, current_datetime, location, link, SITE, description)
            except Exception as e:
                print(f"Oops! Error occured! {e}")
        page_num += 1
    else:
        last_page = False
        break
    print(f"All data Inserted!")



for page_num in range(1, 41):
    pass

# schedule.every().day.at("11:45").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)