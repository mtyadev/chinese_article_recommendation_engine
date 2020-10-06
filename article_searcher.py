# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
from websites import websites
import jieba
import re


class Article():
    def __init__(self, article_url, website, chinese_english_dictionary):
        self.article_url = article_url
        self.website = website
        self.chinese_english_dictionary = chinese_english_dictionary
        self.cached_context_dictionary = self.context_dictionary

    @property
    def content(self):
        res = requests.get(self.article_url)
        soup = BeautifulSoup(res.content, features="html.parser")
        article = soup.find("div", {"id": websites[self.website]}).prettify()
        return article.encode("utf-8")

    @property
    def context_dictionary(self):
        article_tokens = jieba.cut_for_search(self.content)
        return {token.encode("utf-8"): self.chinese_english_dictionary[token.encode("utf-8")] for token in article_tokens
                if token.encode("utf-8", errors="ignore") in self.chinese_english_dictionary}

    @property
    def content_sentences(self):
        res = requests.get(self.article_url)
        soup = BeautifulSoup(res.content, features="html.parser")
        article = soup.find("div", {"id": websites[self.website]}).getText()
        sentences = re.findall(r'[^!?。\.\!\?]+[!?。\.\!\?]?', article)
        return sentences

    @property
    def annotated_sentences(self):
        annotated_sentences = []
        for sentence in self.content_sentences:
            for token in jieba.cut(sentence):
                annotated_sentences.append(self._find_best_dict_match(token))
        return "".join(annotated_sentences).encode().decode('UTF-8')

    def _find_best_dict_match(self, token):
        if token.encode("utf-8", errors="ignore") in self.chinese_english_dictionary:
            # exact match
            return '<a href="#{}">{}</a>'.format(token, token)
        else:
            # find longest match
            original_token = token
            token_list = list(token)
            for _ in range(len(original_token)):
                token_list.pop()
                #print("".join(token_list).encode("utf-8", errors="ignore"))
                if "".join(token_list).encode("utf-8", errors="ignore") in self.chinese_english_dictionary:
                    print("Found SHORTER Match !!!!!!!!!!!!!")
                    # identify leftover parts from original token and run again with this part, iterate
                    #print("FOUND LONGEST MATCH!!!!!!!")
                    return '<a href="#{}">{}</a>'.format("".join(token_list), "".join(token_list))
            return token











