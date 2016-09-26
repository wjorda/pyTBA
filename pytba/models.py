from pytba.util import team_wrap


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

    @team_wrap(pos=1)
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

    @team_wrap(pos=1, format="{}")
    def team_awards(self, team):
        """Gets all of the awards given to this team at this event.
        :param team: (int or str formatted as 'frcXXXX') The team to get awards for.
        :return: A list of dicts (one for each award received), containing:
            award - The detailed award model (see https://www.thebluealliance.com/apidocs#award-model)
            name - String of the award's common name
            awardee - String of the individual recipient of the award (if applicable)
        """
        team = int(team)
        awards = []
        for award in self.awards:
            for recipient in award['recipient_list']:
                if recipient['team_number'] == team:
                    awards.append({'award': award, 'name': award['name'], 'awardee': recipient['awardee']})
        return awards

    @team_wrap(pos=1, format="{}")
    def team_ranking(self, team, array=False):
        """Return the ranking information about a team for this event.
        :param team: (int or str formatted as 'frcXXXX') The team to get ranking information for.
        :param array: (bool) returns info as an array if true, otherwise returns as a dict (default).
        :return: Either an array (array=True) or a dict with the team's ranking information at this event. If returned
            as a dict, the keys will be the headers used for that year's game's ranking table. (See
            https://www.thebluealliance.com/apidocs#event-rankings-request for more info on specific headers usd per year)
            Typically, a team's rank is under "Rank" (capital R).
        """
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

class MatchHelper:
    COMP_LEVEL = 'comp_level'
    MATCH_NUMBER = 'match_number'
    VIDEOS = 'videos'
    TIME_STRING = 'time_string'
    SET_NUMBER = 'set_number'
    EVENT_KEY = 'event_key'
    KEY = 'key'
    TIME = 'time'
    SCORE_BREAKDOWN = 'score_breakdown'
    ALLIANCES = 'alliances'
    BLUE_ALLIANCE = 'alliances/blue'
    BLUE_ALLIANCE_TEAMS = BLUE_ALLIANCE + '/teams'
    BLUE_ALLIANCE_SCORE = BLUE_ALLIANCE + '/score'
    RED_ALLIANCE = 'alliances/red'
    RED_ALLIANCE_TEAMS = RED_ALLIANCE + '/teams'
    RED_ALLIANCE_SCORE = RED_ALLIANCE + '/score'


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

