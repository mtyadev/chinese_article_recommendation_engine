from app import db
from sqlalchemy.orm import relationship

# Below tables are main entities
class CharactersDictionary(db.Model):
    __tablename__ = "characters_dictionary"

    characters = db.Column(db.String, primary_key=True)
    pinyin = db.Column(db.String, nullable=False)
    translation = db.Column(db.String, nullable=False)
    users_character_knowledge = relationship("UsersCharacterKnowledge")
    characters_in_article = relationship("CharactersInArticle")

    def __init__(self, characters, pinyin, translation):
        self.characters = characters
        self.pinyin = pinyin
        self.translation = translation

    def __repr__(self):
        return '<Characters %r>' % self.characters

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    e_mail = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    users_article_assessment = relationship("UsersArticleAssessment")

    def __init__(self, first_name, last_name, e_mail, password):
        self.first_name = first_name
        self.last_name = last_name
        self.e_mail = e_mail
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.e_mail

class Article(db.Model):

    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    overall_rating = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Article %r>' % self.title

# Below tables are bridge tables between main entities above

class UsersCharacterKnowledge(db.Model):

    __tablename__ = "users_character_knowledge"

    characters = db.Column(db.String, db.ForeignKey("characters_dictionary.characters"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    times_seen = db.Column(db.Integer, nullable=False)
    characters_known = db.Column(db.Boolean, nullable=False)
    child = relationship("User")

    def __init__(self, characters, user_id, times_seen, characters_known):
        self.characters = characters
        self.user_id = user_id
        self.times_seen = times_seen
        self.characters_known = characters_known

class UsersArticleAssessment(db.Model):

    __tablename__ = "users_article_assessment"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.String, nullable=False)
    article = relationship("Article")

    def __init__(self, user_id, article_id, rating, difficulty, tags):
        self.user_id = user_id
        self.article_id = article_id
        self.rating = rating
        self.difficulty = difficulty
        self.tags = tags

class CharactersInArticle(db.Model):

    __tablename__ = "characters_in_article"

    characters = db.Column(db.String, db.ForeignKey("characters_dictionary.characters"), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), primary_key=True)
    times_used_in_article = db.Column(db.Integer, nullable=False)
    article = relationship("Article")

    def __init__(self, characters, article_id, times_used_in_article):
        self.characters = characters
        self.article_id = article_id
        self.times_used_in_article = times_used_in_article

    def __repr__(self):
        return '<Characters in Article %r>' % self.characters

class ExampleSentence(db.Model):

    __tablename__ = "example_sentence"

    characters = db.Column(db.String, db.ForeignKey("characters_dictionary.characters"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    sentence = db.Column(db.String, nullable=False)

    def __init__(self, characters, user_id, sentence):
        self.characters = characters
        self.user_id = user_id
        self.sentence = sentence

    def __repr__(self):
        return '<Example Sentence %r>' % self.sentence
