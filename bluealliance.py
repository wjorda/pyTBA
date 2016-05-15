""" Python3 TheBlueAlliance API wrapper for Python 3.

This module serves as a wrapper for the Blue Alliance API for parsing and reading FIRST Robotics Competition event and
team data. This API layer implements LastModified / If-Modified-Since caching for reducing download size and server load.

All clients using this module must call the set_api_key() function before use in order to set the required App ID headers.
"""

import json
import numpy
import requests
from cachecontrol import CacheControl
from cachecontrol.heuristics import LastModified

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


class Event:
    """Class representing a single FRC Event with associated data.

        Attributes (see https://www.thebluealliance.com/apidocs#models for more information):
            key (str): A string of the event's key, usually the year followed by the event code.
            info (dict): Basic information about the event.
            teams (list): A list of team models for each team at the event. (This may include teams who did not
                participate in any matches)
            matches (list): A list of match models for each match at the event.
            awards (list): A list of award models for the awards handed out at the event.
            rankings (list): A 2D table containing the ranking information for the event.
        """

    def __init__(self, info, teams, matches, awards, rankings, filtered=True, key=None):
        """ Constructs an Event object. All required params are the same as specified in the class docstring.
        :param filtered: (bool) Remove from teams any teams that have not played any matches at this event if true
            (default is true).
        :param key: (str) Manual override for the key (if it is not provided in the info dic)
        """
        if key is None and info is not None: self.key = info['key']
        self.info = info
        if filtered:
            self.teams = list(filter(lambda team: len(list(filter(
                lambda match: team['key'] in match['alliances']['red']['teams'] or team['key'] in
                                                                                   match['alliances']['blue']['teams'],
                matches))) > 0, teams))
        else:
            self.teams = teams
        self.matches = sorted(matches, key=match_sort_key)
        self.awards = awards
        self.rankings = rankings

    def get_match(self, match_key):
        """ Gets the specified match.
        :param match_key: (str) The match's individual key (without the event key preceding it)
        :return: A dict containing match information. (see https://www.thebluealliance.com/apidocs#match-model)
        """
        key = self.key + '_' + match_key
        for match in self.matches:
            if match['key'] == key: return match
        return None

    def team_matches(self, team, round=None, quals_only=False, playoffs_only=False):
        """Returns a list of a team's matches at this event.
        :param team: (int or str formatted as 'frcXXXX') The team to get matches for.
        :param round: (str) Competition round to get matches from, either "qualification" or "playoffs"
        :param quals_only: (bool) Select only qualifications if true (default false)
        :param playoffs_only: (bool) Select only playoffs if true (default false, takes precedence over qualsOnly)
        :return: A list of dicts each containing:
            match - a dict with the match model, (See https://www.thebluealliance.com/apidocs#match-model)
            alliance - string containing the teams alliance, either red or blue
            score - int with team's alliance's score
            opp_score - int with team's opponent aliiance's score
        """
        if isinstance(team, int): team = 'frc' + str(team)
        matches = []
        filteredMatches = self.matches

        if (round == 'qualification' or quals_only): filteredMatches = self.get_qual_matches()
        if (round == 'playoffs' or playoffs_only): filteredMatches = self.get_playoff_matches()

        for match in filteredMatches:
            if team in match['alliances']['red']['teams']:
                matches.append({'match': match, 'alliance': 'red', 'score': match['alliances']['red']['score'],
                                'opp_score': match['alliances']['blue']['score']})
            elif team in match['alliances']['blue']['teams']:
                matches.append({'match': match, 'alliance': 'blue', 'score': match['alliances']['blue']['score'],
                                'opp_score': match['alliances']['red']['score']})
        return matches

    def team_awards(self, team):
        """Gets all of the awards given to this team at this event.
        :param team: (int or str formatted as 'frcXXXX') The team to get awards for.
        :return: A list of dicts (one for each award received), containing:
            award - The detailed award model (see https://www.thebluealliance.com/apidocs#award-model)
            name - String of the award's common name
            awardee - String of the individual recipient of the award (if applicable)
        """
        if isinstance(team, str):
            team = int(team.split('frc')[1])
        awards = []
        for award in self.awards:
            for recipient in award['recipient_list']:
                if recipient['team_number'] == team:
                    awards.append({'award': award, 'name': award['name'], 'awardee': recipient['awardee']})
        return awards

    def team_ranking(self, team, array=False):
        """Return the ranking information about a team for this event.
        :param team: (int or str formatted as 'frcXXXX') The team to get ranking information for.
        :param array: (bool) returns info as an array if true, otherwise returns as a dict (default).
        :return: Either an array (array=True) or a dict with the team's ranking information at this event. If returned
            as a dict, the keys will be the headers used for that year's game's ranking table. (See
            https://www.thebluealliance.com/apidocs#event-rankings-request for more info on specific headers usd per year)
            Typically, a team's rank is under "Rank" (capital R).
        """
        if isinstance(team, str):
            team = team.split('frc')[1]
        elif isinstance(team, int):
            team = str(team)
        if not array: headers = self.rankings[0]
        rank = None

        for row in self.rankings:
            if row[1] == team:
                rank = row
                break

        if rank is None: return None
        if array: return rank
        col = 0
        ranking_dict = {}
        for c in headers:
            ranking_dict[c] = rank[col]
            col += 1
        return ranking_dict

    def get_qual_matches(self):
        """Returns the qualification matches for this event."""
        return list(filter(lambda match: match['comp_level'] == 'qm', self.matches))

    def get_playoff_matches(self):
        """Returns the playoff matches for this event."""
        return list(filter(lambda match: match['comp_level'] != 'qm', self.matches))

    def match_matrix(self):
        """Returns a numpy participation matrix for the qualification matches in this event, used for calculating OPR.

            Each row in the matrix corresponds to a single alliance in a match, meaning that there will be two rows (one for
        red, one for blue) per match. Each column represents a single team, ordered by team number. If a team participated
        on a certain alliance, the value at that row and column would be 1, otherwise, it would be 0. For example, an
        event with teams 1-7 that featured a match that pitted teams 1, 3, and 5 against 2, 4, and 6 would have a match
        matrix that looks like this (sans labels):

                                    #1  #2  #3  #4  #5  #6  #7
                        qm1_red     1   0   1   0   1   0   0
                        qm1_blue    0   1   0   1   0   1   0
        """
        match_list = []
        for match in filter(lambda match: match['comp_level'] == 'qm', self.matches):
            matchRow = []
            for team in self.teams:
                matchRow.append(1 if team['key'] in match['alliances']['red']['teams'] else 0)
            match_list.append(matchRow)
            matchRow = []
            for team in self.teams:
                matchRow.append(1 if team['key'] in match['alliances']['blue']['teams'] else 0)
            match_list.append(matchRow)

        mat = numpy.array(match_list)
        return mat[:, numpy.apply_along_axis(numpy.count_nonzero, 0, mat) > 8]

    def opr(self, **kwargs):
        """Calculates component OPRs for all of the teams at this event and returns them as a dict.

        Component OPRs are calculated by solving the overdetermined system team1 + team2 + team3 = alliance statistic for
         all teams at the event. This is done by creating a match matrix A, and then solving Ax = b for each statistic,
         with x being a horizontal vector containing team OPRs, and b a vertical vector containing the alliance statistic.

        Keyworded arguments are either strings (matching the key of the statistic in the score_breakdown for the match)
            or functions (which return a calculated statistic when provided the match model dict and the alliance name).
            Total alliance score is included by default. The results of the OPR calculation are stored in a dict for each
            team, keyed under the team's key in the return dict. The keys in each team's score dict are the same as the
            provided arguments.

        Example:
            tower_strengh_func = lambda match, alliance: 8 - match['score_breakdown']['blue' if alliance == 'red' else 'red']['towerEndStrength']
            oprs = event.opr(teleop='teleopPoints', boulders=tower_strength_func)

            returns:
                {
                    "frc1234": {
                        "score": 55.00 #Total score contribution
                        "teleop": 32.00 #Teleop score contribution
                        "boulders": 5.23 #Tower strength reduction contribution
                    }
                    ....
                }
        """
        match_scores = []
        kwargs['total'] = lambda m, a: match['alliances'][a]['score']
        for match in filter(lambda match: match['comp_level'] == 'qm', self.matches):
            score = []
            for key in kwargs.keys():
                item = kwargs[key]
                if callable(item):
                    score.append(item(match, 'red'))
                else:
                    score.append(match['score_breakdown']['red'][item])
            match_scores.append(score)
            score = []
            for key in kwargs.keys():
                item = kwargs[key]
                if callable(item):
                    score.append(item(match, 'blue'))
                else:
                    score.append(match['score_breakdown']['red'][item])
            match_scores.append(score)

        match_matrix = self.match_matrix()
        score_matrix = numpy.array(match_scores)
        opr_dict = {}
        mat = numpy.transpose(match_matrix).dot(match_matrix)

        for team in self.teams:
            opr_dict[team['key']] = {}

        col = 0
        for key in kwargs:
            """Solving  A'Ax = A'b with A being the match matrix, and b being the score column we're solving for"""
            score_comp = score_matrix[:, col]
            opr = numpy.linalg.solve(mat, numpy.transpose(match_matrix).dot(score_comp))
            assert len(opr) == len(self.teams)
            row = 0
            for team in self.teams:
                opr_dict[team['key']][key] = opr[row]
                row += 1
            col += 1

        return opr_dict


def match_sort_key(match):
    """Function used to sort matches in chronological order, first by level, then by match set.
        Returns a sorting key value for the provided match model.
    """

    levels = {
        'qm': 0,
        'ef': 1000,
        'qf': 2000,
        'sf': 3000,
        'f': 4000
    }

    key = levels[match['comp_level']]
    key += 100 * match['set_number'] if match['comp_level'] != 'qm' else 0
    key += match['match_number']
    return key


def tba_get(path):
    """Base method for querying the TBA API. Returns the response JSON as a python dict.
    :param path: (str) Request path, without the API address prefix (https://www.thebluealliance.com/api/v2/)
    :return: A dict parsed from the response from the API.
    """
    global app_id
    if app_id['X-TBA-App-Id'] == "":
        raise Exception('An API key is required for TBA. Please use set_api_key() to set one.')

    url_str = 'https://www.thebluealliance.com/api/v2/' + path
    r = s.get(url_str, headers=app_id)
    # print(r.url)
    tba_txt = r.text
    return json.loads(tba_txt)


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


def team_get(team):
    """Convenience function for getting team information. Fetches the info dict for the provided team (either an int or
        a string in the form 'frcXXXX')"""
    if isinstance(team, int): team = 'frc' + str(team)
    return tba_get('team/' + team)


def team_events(team, year):
    """Fetches a list of events attended by the provided team (either an int or a string in the form 'frcXXXX') in a
    certain year (int)"""
    if isinstance(team, int): team = 'frc' + str(team)
    return tba_get('team/' + team + '/' + str(year) + '/events')


def team_matches(team, year):
    """Fetches a list of the matches played by the provided team (either an int or a string in the form 'frcXXXX') in a
        certain year (int)"""
    if isinstance(team, int): team = 'frc' + str(team)
    matches = []
    for event in team_events(team, year):
        try:
            ev_matches = tba_get('team/' + team + '/event/' + event['key'] + '/matches')
            for match in ev_matches:
                if team in match['alliances']['red']['teams']:
                    matches.append({'match': match, 'alliance': 'red', 'score': match['alliances']['red']['score'],
                                    'opp_score': match['alliances']['blue']['score']})
                elif team in match['alliances']['blue']['teams']:
                    matches.append({'match': match, 'alliance': 'blue', 'score': match['alliances']['blue']['score'],
                                    'opp_score': match['alliances']['red']['score']})
        except:
            print(event['key'])
    return matches


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


def district_teams(year, district_code):
    """Fetches the list of teams for the provided district (string) in a certain year (int)"""
    return tba_get('district/' + district_code + '/' + str(year) + '/teams')
