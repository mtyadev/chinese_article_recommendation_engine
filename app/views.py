from app import app
from flask import render_template, request
from app.article_searcher import FocusArticle
from training_articles import training_articles
from app.cedict_importer import cleaned_cedict

# Loading Article
article = FocusArticle(training_articles[0][0], training_articles[0][1], cleaned_cedict)

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
            new_db_entry = CharactersDictionary(characters,pinyin,translation)
            db.session.add(new_db_entry)
            db.session.commit()

    return render_template("completed.html", req=req)