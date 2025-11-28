from flask import Flask, render_template, request, url_for, redirect, g, session, flash, abort
from apiUtils import *
from account import *
from logger import *
import sqlite3
import markdown
import os

app = Flask(__name__)
app.secret_key = 'MBIOERMVKLDAFGIOERJGIPERG'

# Logging
init(app)
logs(app)

# Initialisation work
league_ids = [
    "4370",     # Formula 1
    "4413",     # WEC
    "4486"      # Formula 2
]

# League data dictionary
league_data = {}

# Fetch league data for each league
for league in league_ids:
    app.logger.info(f"Getting league data for league {league}")
    league_data.update({league : getLeagueData(app, league)}) 

# Database
db_location = "var/accounts.db"
with app.app_context():
    db = get_db(app)
    with app.open_resource('var/schema.sql', mode='r') as f:
        app.logger.info(f"Executing var/schema.sql")
        db.cursor().executescript(f.read())
    db.commit()

# Articles
articles_location = "articles"

@app.route("/")
def index():

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
    
    return render_template("index.html", title="Home", articles=articles, logged_in = session.get('logged_in', False), username = session.get('username', ''), leagueIds=league_ids, leagues=league_data)

@app.route('/article/<name>')
def article(name):
    app.logger.info(f"Loading article {name}")
    md_path = os.path.join(articles_location, f"{name}.md")

    if not os.path.exists(md_path):
        app.logger.info(f"Couldn't find {md_path}")
        abort(404)

    with open(md_path, "r", encoding="utf-8") as file:
        app.logger.info(f"Opening {md_path}")
        md_text = file.read()

        article_html = markdown.markdown(md_text, extensions=["fenced_code", "tables"])

        return render_template("articles.html", article=article_html, title=name.replace("_", " ").title())  

@app.route('/league')
def leagues():
    leagueId = request.args.get('l', '')

    # No league selected - go home
    if(leagueId == ''):
        return redirect(url_for('index'))

    # Get specific league data
    upcoming_event = getUpcomingEvent(app, leagueId)

    return render_template("league.html", title=league_data[leagueId]["strLeague"],logged_in = session.get('logged_in', False), username = session.get('username', ''), league=league_data[leagueId], nextEvent=upcoming_event)

@app.route('/league/teams')
def leagueTeams():
    leagueId = request.args.get('l', '')

    # No league selected - go home
    if(leagueId == ''):
        return redirect(url_for('index'))
    
    # Get data
    league_teams = getAllLeagueTeams(app, leagueId)
    
    return render_template('teams.html', title=league_data[leagueId]["strLeague"] + " Teams",logged_in = session.get('logged_in', False), username = session.get('username', ''), league=league_data[leagueId], teams=league_teams)

@app.route('/league/team')
def leagueTeamCloseUp():

    # Get url args
    leagueId = request.args.get('l', '')
    teamId = request.args.get('t', '')

    # Invalid url args
    if(leagueId == '' or teamId == ''):
        return redirect(url_for('index'))


@app.route('/league/drivers')
def leagueDrivers():

    # Get url args
    leagueId = request.args.get('l', '')
    teamId = request.args.get('t', '')

    if(teamId == '' or leagueId == ''):
        return redirect(url_for('index'))

    # Get data
    league_drivers = getTeamDrivers(app, leagueId, teamId)

    return render_template('drivers.html', title=league_data[leagueId]["strLeague"] + " Drivers",logged_in = session.get('logged_in', False), username = session.get('username', ''), league=league_data, drivers=league_drivers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']

        if validate_account(app, user, password):
            session['logged_in'] = True
            session['username'] = user

            return redirect(url_for('index'))

    return render_template('login.html', title="Login", logged_in = session.get('logged_in', False), username = session.get('username', ''))

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
            
    return render_template('register.html', title="Register", logged_in = session.get('logged_in', False), username = session.get('username', ''))

# Database stuff
@app.teardown_appcontext
def close_db_connection(app):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()