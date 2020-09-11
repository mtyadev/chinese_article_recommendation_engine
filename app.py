from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from article_searcher import Article
from training_articles import training_articles

app = Flask(__name__)

# Configuring and Intializing the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Setting up the DB Model
class StudyProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    known_characters = db.Column(db.String(200), nullable=False)

# Testing Flask Logic
article = Article(training_articles[0][0], training_articles[0][1])

@app.route('/')
def index():
    return render_template("index.html", article=article, arti)

if __name__ == "__main__":
    app.run(debug=True)

