import requests
from bs4 import BeautifulSoup

from training_articles import training_articles

def get_article(article_url, website):
    res = requests.get(article_url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, features="html.parser")
    article = soup.find("div", {"id": website})
    return article

print(get_article(training_articles[0][0], training_articles[0][1]))
