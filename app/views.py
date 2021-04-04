from app import app, db
from flask import render_template, request
from app.article_searcher import FocusArticle
from training_articles import training_articles
from .models import CharactersDictionary, Article, CharactersInArticle, UsersCharacterKnowledge, UsersArticleAssessment

@app.route('/')
def index():
    return render_template("index.html", training_articles=training_articles)

@app.route('/article', methods = ["GET", "POST"])
def article():
    if request.method == "POST":
        # Load a new article
        article = FocusArticle(request.form.getlist('article')[0], request.form.getlist('website')[0])
    else:
        # Loading one of the recommended articles
        article = FocusArticle(request.args.get('article'), request.args.get('website'))
    return render_template("article.html", article=article.annotated_content, article_id=article.article_id,
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

@app.route('/article_assessment', methods = ["GET", "POST"])
def article_assessment():
    if request.method == "POST":
        article_id = int(request.form.getlist('article_id')[0])
        unknown_characters = request.form.getlist('unknown')
        # !!!Setting TEST USER ID, Replace by Dynamic User ID Later!!!
        user_id = 2
        # !!!END Setting TEST USER ID!!!

        # Get all characters in current article
        characters_in_article = CharactersInArticle.query.filter_by(article_id=article_id).all()

        for dictionary_entry in characters_in_article:
            # Add characters to users_character_knowledge collection in case user sees characters for the first time
            if UsersCharacterKnowledge.query.filter_by(
                    user_id=user_id, characters=dictionary_entry.characters).first() is None:
                if dictionary_entry.characters not in unknown_characters:
                    users_character_knowledge = UsersCharacterKnowledge(dictionary_entry.characters, user_id,
                                                                    dictionary_entry.times_used_in_article, True)
                else:
                    users_character_knowledge = UsersCharacterKnowledge(dictionary_entry.characters, user_id,
                                                                    dictionary_entry.times_used_in_article, False)
                db.session.add(users_character_knowledge)
                db.session.commit()

            # If user has already seen the characters before, update users_character_knowledge related entries
            elif UsersCharacterKnowledge.query.filter_by(
                    user_id=user_id, characters=dictionary_entry.characters).first() is not None:
                existing_users_character_knowledge = UsersCharacterKnowledge.query.filter_by(
                    user_id=user_id, characters=dictionary_entry.characters).first()

                if dictionary_entry.characters not in unknown_characters:
                    existing_users_character_knowledge.times_seen = existing_users_character_knowledge.times_seen + \
                                                                    dictionary_entry.times_used_in_article
                    existing_users_character_knowledge.characters_known = True
                else:
                    existing_users_character_knowledge.times_seen = existing_users_character_knowledge.times_seen + \
                                                                    dictionary_entry.times_used_in_article
                    existing_users_character_knowledge.characters_known = False

                db.session.commit()

    return render_template("article_assessment.html", article_id=article_id)


@app.route('/completed', methods = ["GET", "POST"])
def completed():
    if request.method == "POST":
        article_id = int(request.form.getlist('article_id')[0])
        # !!!Setting TEST USER ID, Replace by Dynamic User ID Later!!!
        user_id = 2
        # !!!END Setting TEST USER ID!!!
        users_article_assessment = UsersArticleAssessment(user_id, article_id, int(request.form.getlist('article_rating')[0]),
                                   int(request.form.getlist('article_difficulty')[0]), request.form.getlist('article_tags')[0])
        db.session.add(users_article_assessment)
        db.session.commit()

    return render_template("completed.html", article_id=article_id)