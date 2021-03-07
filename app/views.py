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
        unknown_characters = request.form.getlist('unknown')
    print("Testing Unknown Characters")
    print(unknown_characters)
    return render_template("check.html", unknown_characters=unknown_characters)

@app.route('/completed', methods = ["GET", "POST"])
def completed():
    if request.method == "POST":
        req = request.form.getlist('unknown')
        for element in req:
            print(element)


    return render_template("completed.html", req=req)