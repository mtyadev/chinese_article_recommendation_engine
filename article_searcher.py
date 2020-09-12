# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
from websites import websites
import jieba


class Article():
    def __init__(self, article_url, website, chinese_english_dictionary):
        self.article_url = article_url
        self.website = website
        self.chinese_english_dictionary = chinese_english_dictionary

    @property
    def content(self):
        res = requests.get(self.article_url)
        soup = BeautifulSoup(res.content, features="html.parser")
        article = soup.find("div", {"id": websites[self.website]}).prettify()
        return article.encode("utf-8")

    @property
    def context_dictionary(self):
        article_tokens = jieba.cut(self.content)
        return {token.encode("utf-8"): self.chinese_english_dictionary[token.encode("utf-8")] for token in article_tokens
                if token.encode("utf-8", errors="ignore") in self.chinese_english_dictionary}




