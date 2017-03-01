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


class TestModelsMethods(unittest.TestCase):
    client = api.TBAClient("WesJordan", "PyTBA-Unit-Test", VERSION)
    event = client.event_get('2016vabla')

    def test__event_init(self):
        event_unfiltered = self.client.event_get('2016vabla', filtered=False)
        self.assertEqual(len(event_unfiltered.teams), len(self.event.teams) - 1)

    def test__event_get_match(self):
        match = self.event.get_match('sf1m2')
        self.assertEqual(match['alliances']['blue']['score'], 115)
        self.assertIsNone(self.event.get_match('an invalid key'))

    def test__event_team_matches(self):


class TestStatsMethods(unittest.TestCase):
    def setUp(self):
        self.tba = api.TBAClient("WesJordan", "PyTBA-Unit-Test", VERSION)
        self.event = self.tba.event_get('2016chcmp')

    def test__opr(self):
        def tower_strength(match, alliance):
            tower = 'red' if alliance == 'blue' else 'blue'
            return 8 - match['score_breakdown'][tower]['towerEndStrength']

        try:
            opr(self.event, invalid_kwarg=6)
            self.fail("Expected ValueError not raised.")
        except ValueError:
            pass

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

    def test__follow_dict_path(self):
        test_dict = {
            'a_list_of_dicts': [
                {'id': 6},
                {'id': 7},
                {'id': 8},
            ],

            'a_dict_of_lists': {
                'fruits': ['apple', 'orange'],
                'veggies': ['broccoli', 'cauliflower']
            },

            'tuple': (1, 2),

            'a_string': 'hello world'
        }

        self.assertEqual(7, util.follow_dict_path(test_dict, 'a_list_of_dicts/1/id'))
        self.assertEqual(['apple', 'orange'], util.follow_dict_path(test_dict, 'a_dict_of_lists/fruits'))
        self.assertEqual(2, util.follow_dict_path(test_dict, 'tuple//1'))
        self.assertEqual('l', util.follow_dict_path(test_dict, 'a_string/3'))

    def test__flip_alliance(self):
        self.assertEqual('blue', util.flip_alliance('red'))
        self.assertEqual('blue', util.flip_alliance('RED'))
        self.assertEqual('red', util.flip_alliance('BLUE'))

        try:
            util.flip_alliance('green')
            self.fail('Expected ValueError not thrown.')
        except ValueError:
            pass

    def test__team_wrap(self):

        @util.team_wrap(pos=(0, 1))
        @util.team_wrap(kword=['three', 'four'])
        def test_func(one, two, three='frc888', four='frc1111'):
            self.assertRegex(one, r"frc[0-9]+.*")
            self.assertRegex(two, r"frc[0-9]+.*")
            self.assertRegex(three, r"frc[0-9]+.*")
            self.assertRegex(four, r"frc[0-9]+.*")

        @util.team_wrap()
        def test_func2(team):
            self.assertRegex(team, r"frc[0-9]+.*")

        test_func('frc1', '2363', three=254)
        test_func(26, '444', four=2114)
        test_func(26, '444', three='203', four=2114)

        test_func2(2354)

        try:
            test_func2('an invalid format')
            self.fail('ValueError expected noy present.')
        except ValueError:
            pass

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
