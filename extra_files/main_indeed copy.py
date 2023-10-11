import random
import requests
from bs4 import BeautifulSoup
import cloudscraper
from urllib.parse import urlencode
API_KEY = '80f8981a-5b43-4472-b3fc-b88b70e59c50'

HEADERS ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}

def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

# r = requests.get(get_scrapeops_url('https://uk.indeed.com/jobs?q=&l=United+Kingdom&fromage=1&vjk=7735c9541c95ecde'))
# r = requests.get('https://uk.indeed.com/jobs?q=&l=United+Kingdom&fromage=1&vjk=7735c9541c95ecde')
# print(r.text)
# soup = BeautifulSoup(r.text, 'lxml')
# get_ol = soup.find_all('h2', attrs={'class': 'jobTitle'})
# for title in get_ol:
#     print(title.text)


HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

r = requests.get('https://uk.indeed.com/jobs?q=&l=United+Kingdom&fromage=1&vjk=7735c9541c95ecde', headers=HEADERS)
print(r.text)
# soup = BeautifulSoup(r.text, 'lxml')
# get_ol = soup.find_all('h2', attrs={'class': 'jobTitle'})
# for title in get_ol:
#     print(title.text)