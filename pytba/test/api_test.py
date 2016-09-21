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


if __name__ == '__main__':
    unittest.main()
