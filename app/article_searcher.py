# -*- coding:utf-8 -*-
from app import db
from .models import CharactersDictionary, Article, CharactersInArticle, UsersCharacterKnowledge
import requests
from bs4 import BeautifulSoup
from websites import websites, headers
import jieba
import re


class FocusArticle():
    def __init__(self, article_url, website):
        self.article_url = article_url
        self.website = website
        self.annotated_content, self.article_id = self.load_content()
        self.context_dictionary = self.create_context_dictionary(self.article_id)

    @property
    def content(self):
        res = requests.get(self.article_url, headers=headers)
        soup = BeautifulSoup(res.content, features="html.parser")
        article = soup.find("div", {websites[self.website][0]: websites[self.website][1]}).getText()
        sentences = re.findall(r'[^!?。\.\!\?]+[!?。\.\!\?]?', article)
        return sentences

    def load_content(self):
        article_id = self._persist_article("test_title", self.article_url, 0)
        annotated_sentences = []
        for sentence in self.content:
            for token in jieba.cut(sentence):
                best_dict_matches = self._find_longest_matches(token, [])
                for best_dict_match in reversed(best_dict_matches):
                    characters_known = "not_seen_yet"
                    cleaned_dict_match = best_dict_match[0].replace("\n", "<br /><br />").strip()
                    if best_dict_match[1] == "available_in_dictionary":

                        characters_already_seen = UsersCharacterKnowledge.query.filter_by(
                            characters=cleaned_dict_match, user_id=2).first()
                        if characters_already_seen:
                            if characters_already_seen.characters_known:
                                characters_known = "already_known"
                            else:
                                characters_known = "not_known_yet"
                        annotated_sentences.append('<a href="#{}" class="{}">{}</a>'.format(
                            cleaned_dict_match, characters_known, cleaned_dict_match))
                        self._persist_characters_in_article(cleaned_dict_match, article_id)
                    else:
                        annotated_sentences.append(cleaned_dict_match)

        return "".join(annotated_sentences).encode().decode("utf-8"), article_id

    def create_context_dictionary(self, article_id):
        return CharactersInArticle.query.filter_by(
            article_id=article_id).join(
            CharactersDictionary, CharactersInArticle.characters == CharactersDictionary.characters).add_columns(
            CharactersDictionary.characters, CharactersDictionary.pinyin, CharactersDictionary.translation).all()

    def _find_longest_matches(self, tokens, searched_in_dictionary=[]):
        """
        Recursive Function, sliding a window from the right most token to the left most token.
        Starting from the right most token expanding the selected tokens token by token to the left most token. Returns the longest
        matching dictionary entry. The longest dictionary entry is then removed from the token list and the same mechanism applied
        recursively to the remaining token list.

        Returns a list containing tuples specifying the tokens and whether or not the specific token is available in the dictionary.
        """
        # If all tokens have been searched in the dictionary return the completed results and leave the function
        print("Searched in Dictionary")
        print(searched_in_dictionary)
        if not tokens:
            return searched_in_dictionary
        # If tokens pre-split by jieba are a direct match, just return this match and leave the function
        # elif CharactersDictionary.query.filter_by(characters=tokens).first():
        #     searched_in_dictionary.append((tokens, "available_in_dictionary"))
        #     return self._find_longest_matches([], searched_in_dictionary)
        else:
            # Create a search window starting with the right most token and iterate over all tokens
            for right_window_edge in range(0, len(tokens)):
                matches = []
                left_window_edge = len(tokens) - 1

                # until the left most token is reached do
                while left_window_edge >= 0:
                    # Append all matching dictionary entries to matches
                    current_selection = "".join(
                        tokens[left_window_edge:-right_window_edge if right_window_edge > 0 else None])
                    if CharactersDictionary.query.filter_by(characters=current_selection).first():
                        matches.append(current_selection)

                    left_window_edge = left_window_edge - 1

                # If there are matches add longest match to list.
                # Remove matching tokens from the list and recursively call function again
                if matches:
                    tokens = tokens[:-len(max(matches, key=len))]
                    # tokens = tokens.replace(max(matches, key=len), "")
                    searched_in_dictionary.append((max(matches, key=len), "available_in_dictionary"))
                    return self._find_longest_matches(tokens, searched_in_dictionary)
                # If there are no matches, append tokens to list, highlighting that they are not available
                else:
                    searched_in_dictionary.append((tokens[right_window_edge-1:], "not_available_in_dictionary"))
                    return self._find_longest_matches(tokens[:-1], searched_in_dictionary)


    # def _find_best_dict_match(self, tokens):
    #     if CharactersDictionary.query.filter_by(characters=tokens).first():
    #         return tokens
    #     else:
    #         # split into groups and find longest matches
    #         longest_matches = []
    #         token_parts = list(tokens)
    #         right_most_token = len(token_parts)
    #         # Sliding a window from right (right most token) in one token steps to the left trying to find the longest dictionary match
    #         for run, token in enumerate(token_parts):
    #             current_window = token_parts[right_most_token-(run + 1): right_most_token]
    #             window_looking_ahead = token_parts[right_most_token-(run + 2):right_most_token]
    #             #Testing Logic Start
    #             print("run\n")
    #             print(run)
    #             print("right_most_token")
    #             print(right_most_token)
    #             print("current_window\n")
    #             print("".join(current_window))
    #             print("window_looking_ahead\n")
    #             print("".join(window_looking_ahead))
    #             print("------------")
    #             #Testing Logic End
    #
    #             # If there is a match in the current window and none in the next wider window looking ahead to the left
    #             if CharactersDictionary.query.filter_by(
    #                     characters="".join(current_window)).first() and \
    #                     CharactersDictionary.query.filter_by(
    #                         characters="".join(window_looking_ahead)).first() is None:
    #                 # Append the found match including the dictionary link
    #                 longest_matches.append("".join(current_window))
    #
    #                 # Testing Logic Start
    #                 print("Returning in first break point")
    #                 # Testing Logic End
    #
    #                 right_most_token = right_most_token - (run + 1)
    #                 run = run + 1
    #
    #             # If the window has reached the left most token and does not find a match
    #             elif run + 1 == right_most_token and \
    #                     CharactersDictionary.query.filter_by(
    #                         characters="".join(current_window)).first() is None:
    #                 # Append without dictionary link
    #                 longest_matches.append("".join(current_window))
    #                 # Testing Logic Start
    #                 print("Returning in second break point")
    #                 # Testing Logic End
    #         return "".join(reversed(longest_matches)).replace("\n", "<br /><br />").strip()

    def _persist_article(self, title, url, overall_rating):
        article = Article(title=title, url=url, overall_rating=overall_rating)
        db.session.add(article)
        db.session.commit()
        return article.id

    def _persist_characters_in_article(self, characters, article_id):
        ignore_list = ["<br /><br />", ""]
        if characters not in ignore_list and CharactersDictionary.query.filter_by(characters=characters).first() is not None:
            if CharactersInArticle.query.filter_by(characters=characters, article_id=article_id).first() is None:
                characters_in_article = CharactersInArticle(characters, article_id, 1)
                db.session.add(characters_in_article)
                db.session.commit()

            elif CharactersInArticle.query.filter_by(characters=characters, article_id=article_id).first():
                existing_characters_in_article = CharactersInArticle.query.filter_by(characters=characters,
                                                                                     article_id=article_id).first()
                existing_characters_in_article.times_used_in_article = existing_characters_in_article.times_used_in_article + 1
                db.session.commit()
















