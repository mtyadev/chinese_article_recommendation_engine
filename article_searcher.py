# -*- coding:utf-8 -*-

import requests
import sys
from bs4 import BeautifulSoup
from websites import websites
import jieba

from cedict_importer import cleaned_cedict
from training_articles import training_articles

def get_article(article_url, website):
    res = requests.get(article_url)
    soup = BeautifulSoup(res.content, features="html.parser")
    article = soup.find("div", {"id": websites[website]})
    return article.encode("utf-8")

def generate_article_dictionary(article, chinese_english_dictionary):
    article_tokens = jieba.cut(article)
    return {token.encode("utf-8"): chinese_english_dictionary[token.encode("utf-8")] for token in article_tokens
            if token.encode("utf-8", errors="ignore") in chinese_english_dictionary}

def main(training_articles, chinese_english_dictionary):
    cleaned_cedict = chinese_english_dictionary
    article = get_article(training_articles[0][0], training_articles[0][1])

    article_dictionary = generate_article_dictionary(article, cleaned_cedict)
    print("\n\nPrinting Article Dictionary")
    print(len(article_dictionary))
    print([str(k).encode("utf-8", errors="ignore") for k, v in article_dictionary.items()])

if __name__ == "__main__":
    main(training_articles, cleaned_cedict)


