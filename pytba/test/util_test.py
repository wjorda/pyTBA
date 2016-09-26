import unittest
import pytba.api as client
from pytba import util, VERSION
from pytba.game_constants import stronghold2016


class MyTestCase(unittest.TestCase):
    def setUp(self):
        client.set_api_key("WesJordan", "PyTBA-Unit-Test", VERSION)

    def test__get_match_stat(self):
        match = client.match_get('2016vabla_qm28')
        self.assertEqual(util.match_stat(match, 'red',
                                         stronghold2016.TELEOP_BOULDERS_HIGH), 0)



if __name__ == '__main__':
    unittest.main()
