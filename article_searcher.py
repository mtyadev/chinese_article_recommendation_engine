import requests
from bs4 import BeautifulSoup
from websites import websites

from training_articles import training_articles

def get_article(article_url, website):
    res = requests.get(article_url)
    soup = BeautifulSoup(res.content, features="html.parser")
    article = soup.find("div", {"id": websites[website]})
    return article.encode("utf-8")

print(get_article(training_articles[0][0], training_articles[0][1]))
