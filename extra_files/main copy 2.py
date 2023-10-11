import requests
from bs4 import BeautifulSoup
import datetime
from db import mycursor, mydb

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
    global total_data_insert_count
    total_data_insert_count += 1
    sql = "INSERT INTO jobs (job_title, posted_date, location, url, site, created_at, updated_at, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (args[0], args[1], args[2], args[3], SITE, args[1], args[1], str(args[4]))
    mycursor.execute(sql, val)
    mydb.commit()
    # print(mycursor.rowcount, "record inserted.")
    print(total_data_insert_count, "record inserted.")

# html_text = requests.get('https://www.cv-library.co.uk/jobs?posted=1&us=1').text


while last_page:
    html_text = requests.get(f"https://www.cv-library.co.uk/jobs?page={page_num}&posted=1&us=1").text
    soup = BeautifulSoup(html_text, 'lxml')
    get_ol = soup.find('ol', attrs = {'class':'results'})
    get_all_lis = get_ol.find_all('li', attrs={'class': 'results__item'})

    check_page_num = soup.find('nav', attrs={'class': 'pagination--center'})
    a_tag_page = check_page_num.find_all('a')
    # Get the href attribute value
    href_page = a_tag_page[-2]['href']
    last_page_index = href_page.split('&')[0].split('=')[-1]
    print(f"page_num===> {page_num}, last_page_index====> {last_page_index}")
    page_links = []
    if page_num != last_page_index:
        for li in get_all_lis:
            a_tag = li.find('a')
            # Get the href attribute value
            href = a_tag['href']
            link = f"{LINK}{href}"
            page_links.append(link)


        for link in page_links:
            try:
                html_text = requests.get(link).text
                soup = BeautifulSoup(html_text, 'lxml')
                heading = soup.find('h1', class_='job__title')
                if heading != None:
                    heading = soup.find('h1', class_='job__title')
                    location = soup.find('dd', attrs={'class': 'job__details-value'})
                    description = soup.find('div', attrs={'class': 'job__description'})
                else: 
                    """
                    else condition run when the heading have different layout
                    """
                    div = soup.find('div', class_='Lidl-info')
                    heading = div.find('h2')
                    location_div = soup.find('div', attrs={'class': 'card--grey mt10'})
                    location = location_div.find_all('dd', attrs={'class': 'job__details-value'})[2]
                    description = soup.find('div', attrs={'class': 'premium-description'})

                heading = ' '.join(heading.text.split()) # removes the extra white spaces from the text
                location = ' '.join(location.text.split()) # removes the extra white spaces from the text
                custom_datetime = date_formated()
                insert_values_into_db(heading, custom_datetime, location, link, description)
            except Exception as e:
                print(f"Oops! Error occured! {e}")
        page_num += 1
    else:
        last_page = False
        break

print("All data Inserted!")