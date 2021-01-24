from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from article_searcher import Article
from training_articles import training_articles
from cedict_importer import cleaned_cedict

app = Flask(__name__)

# Configuring and Intializing the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Setting up the DB Model
class StudyProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    known_characters = db.Column(db.String(200), nullable=False)

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

