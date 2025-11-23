import requests

def getLeagueData(app, leagueId):
    app.logger.info(f"Retrieving league data for league {leagueId}")

    base_url = "https://www.thesportsdb.com/api/v1/json"
    api_key = "123" # Doesn't need to be secure currently - just a free API key

    output = requests.get(base_url + "/" + api_key + "/" + "lookupleague.php?id=" + leagueId)

    try:    
        return output.json()["leagues"][0]
    except:
        return
    
def getUpcomingEvent(app, leagueId):
    app.logger.info(f"Retrieving upcoming event for league {leagueId}")

    base_url = "https://www.thesportsdb.com/api/v1/json"
    api_key = "123" 

    output = requests.get(base_url + "/" + api_key + "/" + "eventsnextleague.php?id=" + leagueId)

    try:
        return output.json()["events"][0]
    except:
        return
    
def getLeagueTeams(app, leagueId):
    app.logger.info(f"Retreiving teams for league {leagueId}")

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    api_key = "123/"
    request = "search_all_teams.php?id="

    output = requests.get(base_url + api_key + request + leagueId)

    try:
        return output.json()
    except:
        return
    
# TODO: Sort this shit out
def getLeagueDrivers(app, leagueId):
    app.logger.info(f"Retreiving drivers for league {leagueId}")

    teams = getLeagueTeams(leagueId)

    output = []

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    api_key = "123/"
    request = "lookup_all_players.php?id="

    for team in teams["teams"]:
        output.append(
            requests.get(base_url + api_key + request + team["idTeam"]).json()
        )

    return output