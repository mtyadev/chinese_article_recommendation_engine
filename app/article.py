# -*- coding:utf-8 -*-
from app import db
from .models import CharactersDictionary, Article, CharactersInArticle, UsersCharacterKnowledge
import jieba
import re

class FocusArticle():
    def __init__(self, unprocessed_content, url):
        self.unprocessed_content = unprocessed_content
        self.url = url
        self.annotated_content, self.article_id = self._annotate_content()
        self.context_dictionary = self.create_context_dictionary(self.article_id)

    @property
    def sentences(self):
        """Split article content into single sentences"""
        sentences = re.findall(r'[^!?。\.\!\?]+[!?。\.\!\?]?', self.unprocessed_content)
        return sentences

    def _annotate_content(self):
        article_id = self._persist_article(self.url)
        annotated_sentences = []
        for sentence in self.sentences:
            annotated_sentences.append("<br /><br />")
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

    def _persist_article(self, url):
        article = Article(url=url)
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
















