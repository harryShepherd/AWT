import requests

def getLeagueData(app, leagueId):
    app.logger.info(f"Retrieving league data for league {leagueId}")

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/lookupleague.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + leagueId).json()
    return output["leagues"][0]
    
def getUpcomingEvent(app, leagueId):
    app.logger.info(f"Retrieving upcoming event for league {leagueId}")

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/eventsnextleague.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + leagueId).json()
    return output["events"]
    
def getAllLeagueTeams(app, leagueId):
    app.logger.info(f"Retreiving teams for league {leagueId}")

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/search_all_teams.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + leagueId).json()
    return output
    
def getLeagueTeam(app, teamId):
    app.logger.info(f"Retreiving data for team {teamId}")

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/lookupteam.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + teamId).json()
    return output["teams"][0]

def getTeam(app, teamId):
    app.logger.info(f"Retreiving team with id {teamId}")
    output = []

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/lookupteam.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + teamId).json()
    return output

def getTeamPlayers(app, teamId):
    app.logger.info(f"Retreiving drivers for team {teamId}")
    output = []

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/lookup_all_players.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + teamId).json()
    return output
    
def getDriver(app, driverId):
    app.logger.info(f"Retreiving info for driver {driverId}")

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/lookupplayer.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + driverId).json()
    return output

def getSeasonSchedule(app, leagueId, seasonYear):
    app.logger.info(f"Retreiving season schedule for {leagueId} and season {seasonYear}")
    output = []

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/eventsseason.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + leagueId + "&s=" + str(seasonYear)).json()

    return sorted(output["events"], key=lambda x:x["strTimestamp"]) 

def getEvent(app, eventId):
    app.logger.info(f"Retreiving event details {eventId}")
    output = []

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/lookupevent.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + eventId).json()

    return output["events"][0]

def getEventResults(app, eventId):
    app.logger.info(f"Retreiving event results {eventId}")
    output = []

    base_url = "https://www.thesportsdb.com/api/v1/json/"
    request = "/eventresults.php?id="
    api_key = app.config['thesportsdb_apikey']

    output = requests.get(base_url + api_key + request + eventId).json()

    return output["results"]