# -*- coding:utf-8 -*-
from app import db
from .models import CharactersDictionary, Article, CharactersInArticle
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
        article = soup.find("div", {"id": websites[self.website]}).getText()
        sentences = re.findall(r'[^!?。\.\!\?]+[!?。\.\!\?]?', article)
        return sentences

    @property
    def annotated_sentences(self):
        article_id = self._persist_article("test_title", self.article_url, 0)
        annotated_sentences = []
        for sentence in self.content:
            for token in jieba.cut(sentence):
                best_dict_match = self._find_best_dict_match(token)
                annotated_sentences.append(best_dict_match)
                self._persist_characters_in_article(best_dict_match, article_id)
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
        if CharactersDictionary.query.filter_by(characters=tokens).first():
            return '<a href="#{}">{}</a>'.format(tokens, tokens)
        else:
            # split into groups and find longest matches
            longest_matches = []
            token_parts = list(tokens)
            search_right_most_token = len(token_parts)
            # Sliding a window from right (search right most token) to left trying to find the longest match
            for run, token in enumerate(token_parts):
                # If there is a match in the current window and none in the next wider window looking ahead to the left
                if CharactersDictionary.query.filter_by(
                        characters="".join(token_parts[len(token_parts)-(run + 1): search_right_most_token])).first() and \
                        CharactersDictionary.query.filter_by(
                            characters="".join(token_parts[len(token_parts)-(run + 2):search_right_most_token])).first() is None:
                    # Append the found match including dictionary link
                    longest_matches.append(
                        '<a href="#{}">{}</a>'.format("".join(
                            token_parts[len(token_parts)-(run + 1):search_right_most_token]), "".join(
                            token_parts[len(token_parts)-(run + 1):search_right_most_token])))
                    search_right_most_token = len(token_parts) - (run + 1)

                # If the window has reached the left most token and does not find a match
                elif run + 1 == len(token_parts) and \
                        CharactersDictionary.query.filter_by(
                            characters="".join(token_parts[len(token_parts)-(run + 1):search_right_most_token])).first() is None:
                    # Append without dictionary link
                    longest_matches.append("".join(token_parts[len(token_parts)-(run + 1):search_right_most_token]))
                for x in reversed(longest_matches):
                    print(x.encode("utf-8"))
            return "".join(reversed(longest_matches)).replace("\n", "<br /><br />").strip()

    @property
    def context_dictionary(self):
        # Replace by database values later
        return {"test".encode("utf-8"): "test".encode("utf-8")}

    def _persist_article(self, title, url, overall_rating):
        article = Article(title=title, url=url, overall_rating=overall_rating)
        db.session.add(article)
        db.session.commit()
        return article.id

    def _persist_characters_in_article(self, characters, article_id):
        ignore_list = ["<br /><br />", ""]
        if characters not in ignore_list:
            import pdb; pdb.set_trace()
            #CharactersInArticle(characters, article_id, times_used_in_article)















