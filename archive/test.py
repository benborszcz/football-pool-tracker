import requests
from bs4 import BeautifulSoup

def fetch_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

url = 'https://www.espn.com/college-football/scoreboard/_/week/1/year/2023/seasontype/3/group/80'
data = fetch_data(url)
print(data.prettify())