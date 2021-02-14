from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os

from article_searcher import Article
from training_articles import training_articles
from cedict_importer import cleaned_cedict

# Loading environment variables
load_dotenv(find_dotenv())
database_user = os.getenv("DB_USER")
database_password = os.getenv("DB_PASSWORD")
database_host = os.getenv("DB_HOST")
database_name = os.getenv("DB_NAME")

app = Flask(__name__)

# Configuring and Intializing the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}/{}'.format(database_user, database_password,
                                                                          database_host, database_name)
db = SQLAlchemy(app)

# Setting up the DB Model

# Below tables are main entities

class CharactersDictionary(db.Model):
    __tablename__ = "characters_dictionary"

    id = db.Column(db.Integer, primary_key=True)
    characters = db.Column(db.String, nullable=False)
    pinyin = db.Column(db.String, nullable=False)
    translation = db.Column(db.String, nullable=False)

    def __init__(self, characters, pinyin, translation, known, times_seen, difficulty_hsk):
        self.characters = characters
        self.pinyin = pinyin
        self.translation = translation
        self.known = known
        self.times_seen = times_seen
        self.difficulty_hsk = difficulty_hsk

    def __repr__(self):
        return '<Characters %r>' % self.characters

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    e_mail = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

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

    characters_dictionary_id = db.Column(db.Integer, db.ForeignKey("characters_dictionary.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    times_seen = db.Column(db.Integer, nullable=False)
    characters_known = db.Column(db.Boolean, nullable=False)

class UsersArticleAssessment(db.Model):

    __tablename__ = "users_article_assessment"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.String, nullable=False)

class CharactersInArticle(db.Model):

    __tablename__ = "characters_in_article"

    characters_dictionary_id = db.Column(db.Integer, db.ForeignKey("characters_dictionary.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)
    times_used_in_article = db.Column(db.Integer, nullable=False)

# Loading Article
article = Article(training_articles[0][0], training_articles[0][1], cleaned_cedict)

@app.route('/')
def index():
    return render_template("index.html", context_dictionary=article.context_dictionary,
                           article=article.annotated_sentences)

@app.route('/check', methods = ["GET", "POST"])
def check():
    if request.method == "POST":
        req = request.form.getlist('unknown')
    return render_template("check.html", req=req, characters_for_db_export=article.characters_for_db_export)

@app.route('/completed', methods = ["GET", "POST"])
def completed():
    if request.method == "POST":
        req = request.form.getlist('unknown')
        for element in req:
            characters = element.split(":")[0]
            pinyin = element.split(":")[1].split(",")[0].replace("'","").replace("(","")
            translation = element.split(":")[1].split(",")[1].replace("'","").replace("(","")
            new_db_entry = Characters(characters,pinyin,translation,False,99999,99999)
            db.session.add(new_db_entry)
            db.session.commit()

    return render_template("completed.html", req=req)

if __name__ == "__main__":
    app.run(debug=True)

