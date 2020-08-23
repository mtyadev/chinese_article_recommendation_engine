# -*- coding:utf-8 -*-

import requests
import sys
from bs4 import BeautifulSoup
from websites import websites
import jieba

from training_articles import training_articles

def get_article(article_url, website):
    res = requests.get(article_url)
    soup = BeautifulSoup(res.content, features="html.parser")
    article = soup.find("div", {"id": websites[website]})
    return article.encode("utf-8")

def tokenizer(article):
    seg_list = jieba.cut(article)
    return " / ".join(seg_list).encode(sys.stdout.encoding, errors='replace')

def main(training_articles):
    article = get_article(training_articles[0][0], training_articles[0][1])
    print(" \n\nPrinting Article")
    print(article)
    article_tokenized = tokenizer(article)
    print("\n\nPrinting Tokens")
    print(article_tokenized.decode("utf8", errors='ignore'))

if __name__ == "__main__":
    main(training_articles)


