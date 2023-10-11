import requests
from bs4 import BeautifulSoup
from datetime import datetime
import mysql.connector
import schedule
import time

BASE_URL = 'https://www.reed.co.uk'
SITE = 'Reed'
last_page = True
total_data_insert_count = 0
url_list = []
page_num = 1

# DB Confiuration
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="cv-library"
)
mycursor = mydb.cursor()


def readable_date_format(date):
    # convert datetime object to desired string format
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")


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
        print(f"SELECT * FROM reed_jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%' AND posted_date = {args[1]}")
        mycursor.execute(f"SELECT * FROM reed_jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%' AND posted_date = '{args[1]}'")
        # fetch all rows returned by the SELECT statement
        result = mycursor.fetchall()
        if len(result) == 0:
            global total_data_insert_count
            total_data_insert_count += 1
            sql = "INSERT INTO reed_jobs (job_title, posted_date, location, url, site, created_at, updated_at, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (args[0], args[1], args[2], args[3], SITE, args[5], args[5], str(args[6]))
            mycursor.execute(sql, val)
            mydb.commit()
            # print(mycursor.rowcount, "record inserted.")
            print(total_data_insert_count, "record inserted.")
        else:
            print("Record Already Exist!")
    except Exception as e:
        print("ERROR: ", e)

# def job():
while last_page:
    print("Starts....")
    # global page_num
    html_text = requests.get(f'https://www.reed.co.uk/jobs?pageno={page_num}&sortby=DisplayDate&datecreatedoffset=Today').text
    soup = BeautifulSoup(html_text, 'lxml')
    try:
        #check if the page is last page 
        find_last_page = soup.find_all('span', class_ = 'widened-criteria-message')[0].text.strip()
        if "Your search for 'Jobs & Vacancies'" in find_last_page:
            break
    except Exception as e:
        articles = soup.find_all('article', class_ = 'job-result-card')
        for article in articles:
            a_tag_page = article.find('a')
            # Get the href attribute value
            href_page = a_tag_page['href']
            print(f"{BASE_URL}{href_page}")
            url_list.append(f"{BASE_URL}{href_page}")
        page_num += 1
print(url_list)
for url in url_list:
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')

    # get the posted date of a Job
    meta_tag = soup.find("meta", itemprop="datePosted")
    posted_date = meta_tag.get("content")
    print(posted_date)
    posted_formated_date = readable_date_format(posted_date)

    #current datetime
    current_date = date_formated_timestamp()
    try:
        main_div = soup.find('div', class_ ='job-info--container')
        job_title = main_div.find('h1').text.strip()
        description = soup.find('div', class_ = 'branded-job--description-container')
        get_location = soup.find('div', class_ = 'job-info--permament-icons')
        location_1 = get_location.find('span', attrs={'data-qa': 'localityLbl'}).text.strip()
        location_2 = get_location.find_all('div')[1].find('span', attrs={'itemprop': 'address'}).find('span', attrs={'itemprop': 'addressLocality'}).text.strip()
        location = f"{location_1}, {location_2}"
        print(f'Job Title: {job_title},\n location: {location}')
        # insert_values_into_db(job_title, posted_formated_date, location, url, SITE, current_date, description)

    except Exception:
        job_title = soup.find('div', class_='job-details').find('h1').text.strip()
        description = soup.find('span', attrs={'itemprop': 'description'})
        location = soup.find('div', class_='location').text.split(',')
        location = location[0].replace('\n', '').strip()+', '+location[1].replace('\\n', '').strip() if len(location) != 1 else location[0].replace('\n', '').strip()
        print(f'Job Title: {job_title},\n location: {location}')
        # insert_values_into_db(job_title, posted_formated_date, location, url, SITE, current_date, description)


# schedule.every().day.at("15:20").do(job)
# schedule.every().day.at("12:53").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)