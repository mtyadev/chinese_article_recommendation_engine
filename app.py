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
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}/{}'.format(database_user, database_password, database_host, database_name)
db = SQLAlchemy(app)

# Setting up the DB Model
class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test = db.Column(db.String(80), unique=True, nullable=False)
    test2 = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<Characters %r>' % self.test

# Loading Article
article = Article(training_articles[0][0], training_articles[0][1], cleaned_cedict)

@app.route('/')
def index():
    return render_template("index.html", context_dictionary=article.context_dictionary,
                           article=article.annotated_sentences)

@app.route('/check', methods = ["GET", "POST"])
def check():
    if request.method == "POST":
        #req = jsonify(request.form.to_dict())
        #req = request.form.getlist('unknown')
        req = request.form.getlist('unknown')
    return render_template("check.html", req=req)

if __name__ == "__main__":
    app.run(debug=True)

