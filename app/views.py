from app import app, db
from flask import render_template, request
from app.article_searcher import FocusArticle
from training_articles import training_articles
from .models import CharactersDictionary, Article, CharactersInArticle, UsersCharacterKnowledge

@app.route('/')
def index():
    # Loading Article
    article = FocusArticle(training_articles[0][0], training_articles[0][1])
    return render_template("index.html", article=article.annotated_content, article_id=article.article_id,
                           context_dictionary=article.context_dictionary)

@app.route('/check', methods = ["GET", "POST"])
def check():
    if request.method == "POST":
        article_id = int(request.form.getlist('article_id')[0])
        unknown_characters_raw = request.form.getlist('unknown')
        unknown_characters = []
        for unknown_character in unknown_characters_raw:
            unknown_characters.append(CharactersDictionary.query.filter_by(characters=unknown_character).first())

    return render_template("check.html", unknown_characters=unknown_characters, article_id=article_id)

@app.route('/completed', methods = ["GET", "POST"])
def completed():
    if request.method == "POST":
        article_id = int(request.form.getlist('article_id')[0])
        unknown_characters = request.form.getlist('unknown')

        # Get all characters in current article
        characters_in_article = CharactersInArticle.query.filter_by(article_id=article_id).all()

        for dictionary_entry in characters_in_article:
            if dictionary_entry.characters not in unknown_characters:
                users_character_knowledge = UsersCharacterKnowledge(dictionary_entry.characters, 1,
                                                                    dictionary_entry.times_used_in_article, True)
            else:
                users_character_knowledge = UsersCharacterKnowledge(dictionary_entry.characters, 1,
                                                                    dictionary_entry.times_used_in_article, False)
            db.session.add(users_character_knowledge)
            db.session.commit()

    return render_template("completed.html", unknown_characters=unknown_characters, article_id=article_id)