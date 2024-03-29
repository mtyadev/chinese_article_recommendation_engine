from app import app, db
import re
from flask import render_template, request
from app.article import FocusArticle
from .models import Article, CharactersDictionary, ExampleSentence, CharactersInArticle, UsersCharacterKnowledge, \
    UsersArticleAssessment
from sqlalchemy import desc

def collect_sample_sentences(characters, user_id, article):
    # Add sample sentences to database for unknown characters
    for sample_sentence in list(set([sentence.replace("\n", "") for sentence in re.findall(
            r'[^!?。\.\!\?]+' + characters + '+.*?[!?。\.\!\?]+', article)])):
        example_sentence = ExampleSentence(characters, user_id, sample_sentence)
        db.session.add(example_sentence)

def update_users_character_knowledge(article, characters_in_article, unknown_characters, user_id):
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
                collect_sample_sentences(dictionary_entry.characters, user_id, article)
            db.session.add(users_character_knowledge)

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
                collect_sample_sentences(dictionary_entry.characters, user_id, article)

def update_article_characters_count(article_characters_count, article_id):
    article = Article.query.filter_by(id=article_id).first()
    article.characters_count = article_characters_count

def get_characters_knowledge_count(characters_known, article_id, user_id):
    characters_knowledge_count = CharactersInArticle.query.join(
        UsersCharacterKnowledge, CharactersInArticle.characters == UsersCharacterKnowledge.characters).filter(
        UsersCharacterKnowledge.user_id == user_id).filter(CharactersInArticle.article_id == article_id).filter(
        UsersCharacterKnowledge.characters_known == characters_known).count()
    return characters_knowledge_count


@app.route('/')
def index():
    characters_to_be_learned = db.engine.execute("""
    SELECT
        uck.characters,
        cd.pinyin,
        cd.translation
        ,count(uck.characters) as times_seen_in_read_articles
    FROM users_character_knowledge as uck
    LEFT JOIN characters_in_article as cia
        ON uck.characters = cia.characters
    LEFT JOIN characters_dictionary as cd
        ON cd.characters = uck.characters
    WHERE characters_known is false
    GROUP BY uck.characters, cd.pinyin, cd.translation
    HAVING count(uck.characters) > 2 
    """)
    characters_to_be_learned = [(
        element,
        ExampleSentence.query.filter_by(
            characters=element.characters).limit(3).all()) for element in characters_to_be_learned]
    article_history = db.session.query(Article, UsersArticleAssessment).join(UsersArticleAssessment).\
        order_by(desc(Article.created_date)).all()
    return render_template("index.html", article_history=article_history,
                           characters_to_be_learned=characters_to_be_learned)

@app.route('/article', methods = ["GET", "POST"])
def article():
    if request.method == "POST":
        # Load a new article
        article = FocusArticle(request.form.getlist('article')[0], request.form.getlist('url')[0])
    return render_template("article.html", article=article.annotated_content, article_id=article.article_id,
                           context_dictionary=article.context_dictionary, focus_article=article.unprocessed_content)

@app.route('/check', methods = ["GET", "POST"])
def check():
    if request.method == "POST":
        article_id = int(request.form.getlist('article_id')[0])
        article = request.form.getlist('focus_article')[0]
        unknown_characters_raw = request.form.getlist('unknown')
        unknown_characters = []
        for unknown_character in unknown_characters_raw:
            unknown_characters.append(CharactersDictionary.query.filter_by(characters=unknown_character).first())

    return render_template("check.html", unknown_characters=unknown_characters, article_id=article_id, focus_article=article)

@app.route('/article_assessment', methods = ["GET", "POST"])
def article_assessment():
    if request.method == "POST":
        article_id = int(request.form.getlist('article_id')[0])
        article = request.form.getlist('focus_article')[0]
        unknown_characters = request.form.getlist('unknown')
        # !!!Setting TEST USER ID, Replace by Dynamic User ID Later!!!
        user_id = 2
        # !!!END Setting TEST USER ID!!!

        # Persist users_character_knowledge and article_characters_count
        update_users_character_knowledge(article, CharactersInArticle.query.filter_by(
            article_id=article_id).all(), unknown_characters, user_id)
        update_article_characters_count(
            CharactersInArticle.query.filter_by(article_id=article_id).count(), article_id)
        db.session.commit()

    return render_template("article_assessment.html", article_id=article_id, focus_article=article)

@app.route('/completed', methods = ["GET", "POST"])
def completed():
    if request.method == "POST":
        article_id = int(request.form.getlist('article_id')[0])
        # !!!Setting TEST USER ID, Replace by Dynamic User ID Later!!!
        user_id = 2
        # !!!END Setting TEST USER ID!!!
        users_article_assessment = UsersArticleAssessment(
            user_id, article_id, int(request.form.getlist('article_rating')[0]),
            int(request.form.getlist('article_difficulty')[0]),
            request.form.getlist('article_tags')[0],
            get_characters_knowledge_count(True, article_id, user_id),
            get_characters_knowledge_count(False, article_id, user_id))
        db.session.add(users_article_assessment)
        db.session.commit()

    return render_template("completed.html", article_id=article_id)