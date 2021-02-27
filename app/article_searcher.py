# -*- coding:utf-8 -*-
from app import db
from .models import CharactersDictionary
import requests
from bs4 import BeautifulSoup
from websites import websites
import jieba
import re

class FocusArticle():
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
        return "".join(annotated_sentences).encode().decode("utf-8")

    @property
    def characters_for_db_export(self):
        soup = BeautifulSoup(self.annotated_sentences, features="html.parser")
        linked_characters = soup.find_all('a', href=True)
        characters_for_db_export = []
        for link in linked_characters:
            characters = link["href"].replace("#", "")
            pinyin = self.chinese_english_dictionary[link["href"].replace("#", "").encode("utf-8")][0]
            translation = self.chinese_english_dictionary[link["href"].replace("#", "").encode("utf-8")][1:]
            difficulty_hsk = "TBD"
            characters_for_db_export.append(DictionaryEntry(characters, pinyin, translation, difficulty_hsk))
        return characters_for_db_export

    def _find_best_dict_match(self, tokens):
        # Testing Query!
        import pdb; pdb.set_trace()
        if True == True:
            #if tokens.encode("utf-8", errors="ignore") in self.chinese_english_dictionary:
            # exact match
            # Testing Query END!
            return '<a href="#{}">{}</a>'.format(tokens, tokens)
        else:
            # split into groups and find longest matches
            longest_matches = []
            token_parts = list(tokens)
            search_right_most_token = len(token_parts)
            # Sliding a window from right (search right most token) to left trying to find the longest match
            for run, token in enumerate(token_parts):
                # If there is a match in the current window and the next bigger window looking ahead to the left is not
                if "".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]).encode("utf-8", errors="ignore") \
                    in self.chinese_english_dictionary \
                    and "".join(token_parts[len(token_parts)-(run + 2):search_right_most_token]).encode("utf-8", errors="ignore")\
                    not in self.chinese_english_dictionary:
                    # Append the found match including dictionary link
                    longest_matches.append('<a href="#{}">{}</a>'.format("".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]), "".join(token_parts[len(token_parts)-(run + 1):search_right_most_token])))
                    search_right_most_token = len(token_parts) - (run + 1)

                # If the window has reached the left most token and does not find a match
                elif run + 1 == len(token_parts) \
                    and "".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]).encode("utf-8", errors="ignore")\
                    not in self.chinese_english_dictionary:
                    # Append without dictionary link
                    longest_matches.append("".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]))
                for x in reversed(longest_matches):
                    print(x.encode("utf-8"))
            return "".join(reversed(longest_matches)).replace("\n","<br /><br />").strip()

    @property
    def context_dictionary(self):
        article_tokens = jieba.cut_for_search(self.content)
        return {token.encode("utf-8"): self.chinese_english_dictionary[token.encode("utf-8")] for token in article_tokens
                if token.encode("utf-8", errors="ignore") in self.chinese_english_dictionary}

class DictionaryEntry():
    def __init__(self, characters, pinyin, translation, difficulty_hsk):
        self.characters = characters
        self.pinyin = pinyin
        self.translation = translation
        self.difficulty_hsk = difficulty_hsk











