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

    def _find_best_dict_match(self, tokens):
        if tokens.encode("utf-8", errors="ignore") in self.chinese_english_dictionary:
            # exact match
            return '<a href="#{}">{}</a>'.format(tokens, tokens)
        else:
            # split into groups and find longest matches
            longest_matches = []
            token_parts = list(tokens)
            search_right_most_token = len(token_parts)
            for run, token in enumerate(token_parts):
                if "".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]).encode("utf-8", errors="ignore") in self.chinese_english_dictionary:
                    longest_matches.append('<a href="#{}">{}</a>'.format("".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]), "".join(token_parts[len(token_parts)-(run + 1):search_right_most_token])))
                    search_right_most_token = len(token_parts) - (run + 1)
                elif run + 1 == len(token_parts) and "".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]).encode("utf-8", errors="ignore") not in self.chinese_english_dictionary:
                    longest_matches.append("".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]))

            return "".join(reversed(longest_matches))










