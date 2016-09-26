import unittest
import pytba.api as tba
from pytba import VERSION
from pytba.stats import opr


class MyTestCase(unittest.TestCase):
    def setUp(self):
        tba.set_api_key("WesJordan", "PyTBA-Unit-Test", VERSION)
        self.event = tba.event_get('2016chcmp')

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


if __name__ == '__main__':
    unittest.main()
