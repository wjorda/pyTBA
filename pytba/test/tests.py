import unittest

import util
from game_constants import stronghold2016
from pytba import api, VERSION
from stats import opr


class TestApiMethods(unittest.TestCase):
    client = api.TBAClient("WesJordan", "PyTBA-Unit-Test", VERSION)

    def test__tba_get(self):
        # Query with proper key should succeed
        team = self.client.tba_get('team/frc2363')
        self.assertEqual(team['key'], 'frc2363')

        # Query with invalid key should fail
        with self.assertRaises(TypeError):
            self.client.set_api_key('invalid_key', None, None)
            self.client.tba_get('team/frc2363')

    def test__event_get(self):
        event = self.client.event_get('2016tes')
        self.assertEqual(len(event.teams), 75)
        self.assertEqual(event.info['name'], 'Tesla Division')
        self.assertEqual(len(event.matches), 140)
        self.assertEqual(event.rankings[1][1], '2056')

    def test__team_matches(self):
        matches = self.client.team_matches('frc2363', 2016)
        self.assertEqual(len(matches), 81)
        self.assertEqual(matches[-1]['alliances']['opponent']['score'], 89)


class TestStatsMethods(unittest.TestCase):
    def setUp(self):
        self.tba = api.TBAClient("WesJordan", "PyTBA-Unit-Test", VERSION)
        self.event = self.tba.event_get('2016chcmp')

    def test__opr(self):
        def tower_strength(match, alliance):
            tower = 'red' if alliance == 'blue' else 'blue'
            return 8 - match['score_breakdown'][tower]['towerEndStrength']

        oprs = opr(self.event, alt_score='/alliances/##ALLIANCE/score', teleop='teleopPoints', boulders=tower_strength)
        record = oprs['frc1418']
        self.assertAlmostEqual(record['total'], 41.90, places=2)
        self.assertAlmostEqual(record['alt_score'], 41.90, places=2)
        self.assertAlmostEqual(record['boulders'], 3.95, places=2)
        self.assertAlmostEqual(record['teleop'], 29.30, places=2)

        old = self.tba.event_get('2006md')
        oprs = opr(old, dpr='/alliances/##OPPALLIANCE/score')
        record = oprs['frc303']
        self.assertAlmostEqual(record['total'], 19.26, places=2)
        self.assertAlmostEqual(record['dpr'], 14.94, places=2)


class TestUtilMethods(unittest.TestCase):
    client = api.TBAClient("WesJordan", "PyTBA-Unit-Test", VERSION)

    def test__get_match_stat(self):
        match = self.client.match_get('2016vabla_qm28')
        self.assertEqual(util.match_stat(match, 'red',
                                         stronghold2016.TELEOP_BOULDERS_HIGH), 5)

    def test__list2dict(self):
        mylist = [
            {'id': 'a', 'apples': 2, 'cherries': 3},
            {'id': 'b', 'apples': 4, 'cherries': 6},
            {'id': 'c', 'apples': 6, 'cherries': 9},
            {'id': 'd', 'apples': 8, 'cherries': 12},
        ]

        mydict1 = util.list2dict(mylist)
        mydict2 = util.list2dict(mylist, 'id')
        mydict3 = util.list2dict(mylist, ['John Doe', 'Jane Doe', 'Alice', 'Bob'])
        mydict4 = util.list2dict(mylist, lambda item: item['id'] * 2)
        apples = [mydict1[item]['apples'] for item in mydict1]

        self.assertCountEqual(apples, [2, 4, 6, 8])
        self.assertCountEqual(mydict2.keys(), ['a', 'b', 'c', 'd'])
        self.assertCountEqual(mydict3.keys(), ['John Doe', 'Jane Doe', 'Alice', 'Bob'])
        self.assertCountEqual(mydict4.keys(), ['aa', 'bb', 'cc', 'dd'])


if __name__ == '__main__':
    unittest.main()
