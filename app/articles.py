import sqlite3
from flask import g
import os

db_location = 'var/article-comments.db'
articles_location = 'static/articles'

def get_all_articles(app):
    articles = []

    # Get the list of articles
    for filename in os.listdir(articles_location):
        if filename.endswith(".md"):
            name = filename[:-3]
            title = name.replace("_", " ")
            articles.append({
                "name": name,
                "title": title.title()
            })

    return articles

def initialise_article_db(app):
    article_db = get_article_comments_db(app)
    with app.open_resource('var/article_schema.sql', mode='r') as f:
        app.logger.info(f"Executing var/article_schema.sql")
        article_db.cursor().executescript(f.read())

def get_article_comments_db(app):
    app.logger.info("Retrieving article comments database")

    db = getattr(g, 'articles_db', None)
    if db is None:
        db = sqlite3.connect(db_location)
        g.articles_db = db
    return db

def get_total_comments(app, articleName):
    app.logger.info(f"Getting total comments for article {articleName}")
    
    db = get_article_comments_db(app)

    result = db.cursor().execute(f"SELECT COUNT(*) FROM article_comments WHERE article_comments.article_name='{articleName}'")

    return result.fetchall()[0][0]

def get_comments(app, articleName):
    app.logger.info(f"Getting comments for article {articleName}")
    
    db = get_article_comments_db(app)

    result = db.cursor().execute(f"SELECT * FROM article_comments WHERE article_comments.article_name='{articleName}' ORDER BY comment_timestamp DESC")

    return result.fetchall()

def create_comment(app, articleName, commentString, username, timestamp):
    app.logger.info(f"{username} added a comment to {articleName}: {commentString}")

    db = get_article_comments_db(app)

    stmnt = f"INSERT INTO article_comments VALUES ('{commentString}', '{articleName}', '{username}', '{timestamp}')"

    try:
        db.execute(stmnt)
        db.commit()
        app.logger.info("Success")
    except:
        app.logger.info("Failed")
        return False
    
    return True