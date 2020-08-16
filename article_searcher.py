import requests
from bs4 import BeautifulSoup

from websites import websites

def get_article(article_url, website):
    res = requests.get(article_url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text)
    article = soup.find("div", {"id": websites[website]})
    return article
