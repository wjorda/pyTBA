import unittest

from pytba import VERSION
from pytba import api as client

class TestApiMethods(unittest.TestCase):
    def setUp(self):
        client.set_api_key("WesJordan", "PyTBA-Unit-Test", VERSION)

    def test__tba_get(self):
        # Query with proper key should succeed
        team = client.tba_get('team/frc2363')
        self.assertEqual(team['key'], 'frc2363')

        # Query with invalid key should fail
        with self.assertRaises(TypeError):
            client.tba_get('team/frc2363', app_id='invalid key')

    def test__event_get(self):
        event = client.event_get('2016tes')
        self.assertEqual(len(event.teams), 75)
        self.assertEqual(event.info['name'], 'Tesla Division')
        self.assertEqual(len(event.matches), 140)
        self.assertEqual(event.rankings[1][1], '2056')

    def test__team_matches(self):
        matches = client.team_matches('frc2363', 2016)
        self.assertEqual(len(matches), 62)
        self.assertEqual(matches[-1]['alliances']['opponent']['score'], 89)

if __name__ == '__main__':
    unittest.main()
