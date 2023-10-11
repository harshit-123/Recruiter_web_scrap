import requests
from bs4 import BeautifulSoup
from datetime import datetime
import mysql.connector
import logging

BASE_URL = 'https://www.reed.co.uk'
SITE = 'Reed'
last_page = True
total_data_insert_count = 0
# url_list = []
page_num = 1


#log file
log_file = "reed_cron_error_log.txt"
logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# DB Confiuration
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="jobs"
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
        # print(f"SELECT * FROM jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%' AND posted_date = {args[1]}")
        mycursor.execute(f"SELECT * FROM jobs WHERE job_title LIKE '%{args[0]}%' AND location LIKE '%{args[2]}%' AND posted_date = '{args[1]}'")
        # fetch all rows returned by the SELECT statement
        result = mycursor.fetchall()
        if len(result) == 0:
            global total_data_insert_count
            total_data_insert_count += 1
            sql = "INSERT INTO jobs (job_title, posted_date, location, url, site, created_at, updated_at, description, unique_job_no) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            print(sql)
            location_without_quote = args[2].replace("'", "")
            title = args[0].replace("'", "")
            val = (title, args[1], location_without_quote, args[3], SITE, args[5], args[5], str(args[6]), 0)
            mycursor.execute(sql, val)
            mydb.commit()
            # print(mycursor.rowcount, "record inserted.")
            #print(total_data_insert_count, "record inserted.")
        else:
            pass
            #print("Record Already Exist!")
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        print("ERROR: ", e)


def grab_jobs_fields(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')

    # get the posted date of a Job
    meta_tag = soup.find("meta", itemprop="datePosted")
    posted_date = meta_tag.get("content")
    # print(posted_date)
    posted_formated_date = readable_date_format(posted_date)

    #current datetime
    current_date = date_formated_timestamp()
    try:
        get_reed_jobs(soup, posted_formated_date, url, current_date)
    except Exception:
        get_reed_jobs_different_format(soup, posted_formated_date, url, current_date)


#Rename this here and in `get_job`
def get_reed_jobs(soup, posted_formated_date, url, current_date):
    main_div = soup.find('div', class_ ='job-info--container')
    job_title = main_div.find('h1').text.strip()
    description = soup.find('div', class_ = 'branded-job--description-container')
    get_location = soup.find('div', class_ = 'job-info--permament-icons')
    location_1 = get_location.find('span', attrs={'data-qa': 'localityLbl'}).text.strip()
    location_2 = get_location.find_all('div')[1].find('span', attrs={'itemprop': 'address'}).find('span', attrs={'itemprop': 'addressLocality'}).text.strip()
    location = f"{location_1}, {location_2}"
    # print(f'Job Title: {job_title},\n location: {location}')
    insert_values_into_db(job_title, posted_formated_date, location, url, SITE, current_date, description, 0)


#Rename this here and in `get_job`
def get_reed_jobs_different_format(soup, posted_formated_date, url, current_date):
    job_title = soup.find('div', class_='job-details').find('h1').text.strip()
    description = soup.find('span', attrs={'itemprop': 'description'})
    location = soup.find('div', class_='location').text.split(',')
    location = location[0].replace('\n', '').strip()+', '+location[1].replace('\\n', '').strip() if len(location) != 1 else location[0].replace('\n', '').strip()
    # print(f'Job Title: {job_title},\n location: {location}')
    insert_values_into_db(job_title, posted_formated_date, location, url, SITE, current_date, description, 0)


def main():
    global page_num
    while last_page:
        try:
            #html_text = requests.get(f'https://www.reed.co.uk/jobs?pageno={page_num}&sortby=DisplayDate&datecreatedoffset=Today').text
            html_text = requests.get(f'https://www.reed.co.uk/jobs?sortBy=displayDate&pageno={page_num}&dateCreatedOffSet=today').text
            soup = BeautifulSoup(html_text, 'lxml')
            #check if the page is last page
            navigation = soup.find('nav', attrs={'role': 'navigation'})
            try:
                get_next_page_lis = navigation.find_all('li', attrs={'class': 'page-item disabled'})[-1]
                print("l1===>", get_next_page_lis)
            except Exception as e:
                logging.error("An error occurred: %s", str(e))
            if get_next_page_lis.find('span') is None:
                break
            # articles = soup.find_all('article', class_ = 'job-card_jobCard__B4kku')
            articles = soup.find_all('article', attrs={'data-qa': 'job-card'})
            for article in articles:
                post_link = article.find('a')['href']
                url = f"{BASE_URL}{post_link}"
                # url_list.append(f"{BASE_URL}{post_link}")
                grab_jobs_fields(url)
            page_num += 1
        except Exception as e:
            print("ERROR", e)
            logging.error("An error occurred: %s", str(e))

#if _name_ == '__main__':
    #main()
main()
