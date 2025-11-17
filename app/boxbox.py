from flask import Flask, render_template, request, url_for, redirect
import requests

app = Flask(__name__)

def get_league_data(leagueId):
    base_url = "https://www.thesportsdb.com/api/v1/json"
    api_key = "123" # Doesn't need to be secure currently - just a free API key

    output = requests.get(base_url + "/" + api_key + "/" + "lookupleague.php?id=" + leagueId)

    try:    
        return output.json()["leagues"][0]
    except:
        return -1

@app.route("/")
def index():

    league_ids = [
        get_league_data("4370"),    # Formula 1
        get_league_data("4413"),    # WEC
        get_league_data("4486")     # Formula 2
    ]

    return render_template("index.html", title="Home", leagues=league_ids)

@app.route('/league/')
def leagues():
    leagueId = request.args.get('id', '')

    if(leagueId == ''):
        return redirect(url_for('index'))

    league_data = get_league_data(leagueId)

    return render_template("league.html", title=league_data["strLeague"], league=league_data)