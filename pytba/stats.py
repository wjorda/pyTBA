import numpy

from pytba.models import Event


def match_matrix(event: Event):
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
    for match in filter(lambda match: match['comp_level'] == 'qm', event.matches):
        matchRow = []
        for team in event.teams:
            matchRow.append(1 if team['key'] in match['alliances']['red']['teams'] else 0)
        match_list.append(matchRow)
        matchRow = []
        for team in event.teams:
            matchRow.append(1 if team['key'] in match['alliances']['blue']['teams'] else 0)
        match_list.append(matchRow)

    mat = numpy.array(match_list)
    return mat[:, numpy.apply_along_axis(numpy.count_nonzero, 0, mat) > 8]


def opr(event: Event, **kwargs):
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
    for match in filter(lambda match: match['comp_level'] == 'qm', event.matches):
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

    match_matrix = event.match_matrix()
    score_matrix = numpy.array(match_scores)
    opr_dict = {}
    mat = numpy.transpose(match_matrix).dot(match_matrix)

    for team in event.teams:
        opr_dict[team['key']] = {}

    col = 0
    for key in kwargs:
        """Solving  A'Ax = A'b with A being the match matrix, and b being the score column we're solving for"""
        score_comp = score_matrix[:, col]
        opr = numpy.linalg.solve(mat, numpy.transpose(match_matrix).dot(score_comp))
        assert len(opr) == len(event.teams)
        row = 0
        for team in event.teams:
            opr_dict[team['key']][key] = opr[row]
            row += 1
        col += 1

    return opr_dict
