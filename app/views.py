from app import app
from flask import render_template, request
from app.article_searcher import FocusArticle
from training_articles import training_articles

# Loading Article
article = FocusArticle(training_articles[0][0], training_articles[0][1])

@app.route('/')
def index():
    annotated_article, article_id = article.load_content()
    context_dictionary = article.create_context_dictionary(article_id)
    return render_template("index.html", article=annotated_article, context_dictionary=context_dictionary)

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