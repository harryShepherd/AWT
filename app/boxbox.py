import datetime
from flask import Flask, render_template, request, url_for, redirect, g, session, flash, abort
from apiUtils import *
from account import *
from articles import *
from logger import *
import sqlite3
import markdown
import os

app = Flask(__name__)

# Logging
init(app)
logs(app)

app.secret_key = app.config['secretkey']

# Initialisation work
league_ids = [
    "4370",     # Formula 1
    "4413",     # WEC
    "4486",     # Formula 2
    "4371",     # Formula E
    "4407",     # Moto GP
    "4373",     # IndyCar
]

# League data dictionary
league_data = {}

# Fetch league data for each league
for league in league_ids:
    app.logger.info(f"Getting league data for league {league}")
    league_data.update({league : getLeagueData(app, league)}) 

# Databases
with app.app_context():
    initialise_account_db(app)
    initialise_article_db(app)
    initialise_event_db(app)

@app.route("/")
def index():

    articles = get_all_articles(app)
    
    return render_template(
        "index.html",
        title="Home",
        articles=articles,
        logged_in = session.get('logged_in', False),
        username = session.get('username', ''),
        leagueIds=league_ids,
        leagues=league_data
        )

@app.route('/article/<name>', methods=['GET', 'POST'])
def article(name):

    if request.method == 'POST':
        # Check if we're logged in
        if session.get('logged_in', False):
            # Get the comment
            commentString = request.form['comment-box']
            commentTimestamp = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")

            # Create the comment
            if not create_article_comment(app, name, commentString, session.get('username', ''), commentTimestamp):
                # We failed
                app.logger.info(f"Failed to create comment on {name}")
            else:
                # We succeeded
                app.logger.info(f"Successfully published comment to article {name}")
        else:
            app.logger.info(f"Tried to leave a comment without being logged in.")

    app.logger.info(f"Loading article {name}")

    # Get the article path
    md_path = os.path.join(articles_location, f"{name}.md")

    if not os.path.exists(md_path):
        app.logger.info(f"Couldn't find {md_path}")
        abort(404)

    with open(md_path, "r", encoding="utf-8") as file:
        app.logger.info(f"Opening {md_path}")
        md_text = file.read()

    file.close()

    # Convert the markdown into html
    article_html = markdown.markdown(md_text, extensions=["fenced_code", "tables"])

    # Get the number of comments on this article
    total_comments = get_total_article_comments(app, name)

    # Get the  comments
    comments = get_article_comments(app, name)

    return render_template(
        "articles.html",
        title=name.replace("_", " ").title(),
        article=article_html,
        total_comments=total_comments,
        comments=comments,
        logged_in = session.get('logged_in', False),
        username = session.get('username', '')
    )

@app.route('/league')
def leagues():
    leagueId = request.args.get('l', '')

    # No league selected - go home
    if(leagueId == ''):
        return redirect(url_for('index'))

    # Get specific league data
    upcoming_event = getUpcomingEvent(app, leagueId)
    league_teams = getAllLeagueTeams(app, leagueId)

    if leagueId == '4371':
        schedule = getSeasonSchedule(app, leagueId, '2025-2026')
    else:
        schedule = getSeasonSchedule(app, leagueId, 2025)

    return render_template(
        "league.html",
        title=league_data[leagueId]["strLeague"],
        logged_in = session.get('logged_in', False),
        username = session.get('username', ''),
        league=league_data[leagueId],
        teams=league_teams,
        nextEvent=upcoming_event,
        schedule=schedule
        )

@app.route('/team')
def leagueTeamCloseUp():

    # Get url args
    teamId = request.args.get('t', '')

    # Invalid url args
    if(teamId == ''):
        return redirect(url_for('index'))
    
    # Get data
    team = getTeam(app, teamId)
    drivers = getTeamPlayers(app, teamId)

    return render_template(
        'team.html',
        title=team["teams"][0]["strTeam"],
        logged_in = session.get('logged_in', False),
        username = session.get('username', ''),
        team=team,
        drivers=drivers
        )

@app.route('/driver')
def individualDriver():

    # Get url args
    driverId = request.args.get('d', '')

    if(driverId == ''):
        return redirect(url_for('index'))
    
    # Get data
    driver_data = getDriver(app, driverId)['players'][0]

    return render_template(
        'driver.html',
        title="",
        logged_in = session.get('logged_in', False),
        username=session.get('username', ''),
        driver=driver_data
        )

@app.route('/event', methods=['GET', 'POST'])
def event():

    # Get URL args
    eventId = request.args.get('e', '')

    if eventId == '':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Check if we're logged in
        if session.get('logged_in', False):
            # Get the comment
            commentString = request.form['comment-box']
            commentTimestamp = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")

            # Create the comment
            if not create_event_comment(app, eventId, commentString, session.get('username', ''), commentTimestamp):
                # We failed
                app.logger.info(f"Failed to create comment on event {eventId}")
            else:
                # We succeeded
                app.logger.info(f"Successfully published comment to event {eventId}")
        else:
            app.logger.info(f"Tried to leave a comment without being logged in.")

    # Get data
    event_data = getEvent(app, eventId)

    total_comments = get_total_event_comments(app, eventId)

    comments = get_event_comments(app, eventId)

    results = getEventResults(app, eventId)

    return render_template(
        'event.html',
        title="",
        logged_in = session.get('logged_in', False),
        username=session.get('username', ''),
        event=event_data,
        total_comments=total_comments,
        comments=comments,
        results=results
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']

        if validate_account(app, user, password):
            session['logged_in'] = True
            session['username'] = user

            return redirect(url_for('index'))

    return render_template(
        'login.html',
        title="Login",
        logged_in = session.get('logged_in', False),
        username = session.get('username', '')
        )

@app.route('/logout')
def logout():
    session['username'] = ''
    session['logged_in'] = False

    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        app.logger.info(f"Received register request with username: {username}, email: {email}")

        if not register_account(app, username, email, password):
            app.logger.info(f"Failed to register account  with username: {username}, email: {email}")
        else:
            app.logger.info(f"Registered account with username: {username}, email: {email}")
            
    return render_template(
        'register.html',
        title="Register",
        logged_in = session.get('logged_in', False),
        username = session.get('username', '')
        )

@app.route('/account')
def account():
    user = request.args.get('user', '')

    return render_template(
        'account.html',
        title=user,
        logged_in = session.get('logged_in', False),
        username = session.get('username'),
        account = user
    )

# Database stuff
@app.teardown_appcontext
def close_db_connection(app):
    accounts_db = getattr(g, 'accounts_db', None)
    if accounts_db is not None:
        accounts_db.close()
        
    articles_db = getattr(g, 'articles_db', None)
    if articles_db is not None:
        articles_db.close()