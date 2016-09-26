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
