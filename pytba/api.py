""" Python3 TheBlueAlliance API wrapper for Python 3.

This module serves as a wrapper for the Blue Alliance API for parsing and reading FIRST Robotics Competition event and
team data. This API layer implements LastModified / If-Modified-Since caching for reducing download size and server load.

All clients using this module must call the set_api_key() function before use in order to set the required App ID headers.
"""

import json
import requests
from cachecontrol import CacheControl
from cachecontrol.heuristics import LastModified

from pytba.models import Event
from pytba.util import team_wrap

__author__ = "Wes Jordan"

app_id = {'X-TBA-App-Id': ""}
s = requests.Session()
s = CacheControl(s, heuristic=LastModified())
s.headers.update(app_id)


def set_api_key(name, description, version):
    """Sets the required API headers for the TBA API. This function MUST be
        called in order to use the API.

    :param name: (str) User of team name
    :param description: (str) Name of the program using the API
    :param version: Program version.
    """
    global app_id
    app_id['X-TBA-App-Id'] = name + ':' + description + ':' + str(version)


def tba_query(path_func, app_id=app_id):
    def query(*args):
        path_str = path_func(*args)
        return tba_get(path_str, app_id)

    return query


def tba_get(path, app_id=app_id):
    """Base method for querying the TBA API. Returns the response JSON as a python dict.
    :param path: (str) Request path, without the API address prefix (https://www.thebluealliance.com/api/v2/)
    :param app_id: (str) TBA App ID. Defaults to the module-wide ID
    :return: A dict parsed from the response from the API.
    """

    if app_id['X-TBA-App-Id'] == "":
        raise Exception('An API key is required for TBA. Please use set_api_key() to set one.')

    url_str = 'https://www.thebluealliance.com/api/v2/' + path
    r = s.get(url_str, headers=app_id)
    # print(r.url)
    tba_txt = r.text
    try:
        return json.loads(tba_txt)
    except json.JSONDecodeError:
        print(url_str)
        print(tba_txt)


def event_get(year_key, filtered=True):
    """Returns an Event object for the provided key, fetching the required data from the API.
    :param year_key: (str) The key for the event in the form of the year followed by the event code. (E.g. 2016scmb)
    :param filtered: Remove no-show (teams who have played no matches) teams from the team list (required to calculate OPR)
    :return:
    """
    event_url = 'event/' + year_key + '/'
    info = tba_get(event_url[:-1])
    teams = tba_get(event_url + 'teams')
    matches = tba_get(event_url + 'matches')
    awards = tba_get(event_url + 'awards')
    rankings = tba_get(event_url + 'rankings')
    return Event(info, teams, matches, awards, rankings, key=year_key, filtered=filtered)


@team_wrap()
@tba_query
def team_get(team):
    """Convenience function for getting team information. Fetches the info dict for the provided team (either an int or
        a string in the form 'frcXXXX')"""
    return 'team/' + team


@team_wrap()
@tba_query
def team_events(team, year):
    """Fetches a list of events attended by the provided team (either an int or a string in the form 'frcXXXX') in a
    certain year (int)"""
    return 'team/' + team + '/' + str(year) + '/events'


@team_wrap()
def team_matches(team, year):
    """Fetches a list of the matches played by the provided team (either an int or a string in the form 'frcXXXX') in a
        certain year (int)"""
    matches = []
    for event in team_events(team, year):
        try:
            ev_matches = tba_get('team/' + team + '/event/' + event['key'] + '/matches')
            for match in ev_matches:
                if team in match['alliances']['red']['teams']:
                    team_color = 'red'
                    oppo_color = 'blue'
                elif team in match['alliances']['blue']['teams']:
                    team_color = 'blue'
                    oppo_color = 'red'

                match['alliances']['team'] = match['alliances'][team_color]
                match['score_breakdown']['team'] = match['score_breakdown'][team_color]
                match['alliances']['opponent'] = match['alliances'][oppo_color]
                match['score_breakdown']['opponent'] = match['score_breakdown'][oppo_color]
                matches.append(match)
        except:
            print(event['key'])
            raise
    return matches


@tba_query
def match_get(match_key):
    return 'match/' + match_key


def district_list(year):
    """Fetches the key/name list of active districts in a certain year (int)"""
    dists = tba_get('districts/' + str(year))
    districts = {}
    for dist in dists:
        districts[dist['key']] = dist['name']
    return districts


def district_events(year, district_code):
    """Fetches the list of events for the provided district (string) in a certain year (int)"""
    return tba_get('district/' + district_code + '/' + str(year) + '/events')


def district_rankings(year, district_code, team=None):
    """Fetches the district standings for a given year
    :param year: (int) Year to fetch standings from
    :param district_code: (str) District code to get standings from
    :param team: (optional) (int or str formatted 'frcXXXX')
    :return: If no team specified, a list with the points breakdown for each team in the district
        (see https://www.thebluealliance.com/apidocs#district-rankings-request), sorted by total points. If a team is
        specified, returns only the breakdown for that team.
    """
    if isinstance(team, int): team = 'frc' + str(team)
    ranks_list = []
    ranks_dict = tba_get('district/' + district_code + '/' + str(year) + '/rankings')
    for row in ranks_dict:
        if team is not None and row['team_key'] == team:
            return row
        elif team is None:
            ranks_list.append(row)
    return ranks_list


@tba_query
def district_teams(year, district_code):
    """Fetches the list of teams for the provided district (string) in a certain year (int)"""
    return 'district/' + district_code + '/' + str(year) + '/teams'
