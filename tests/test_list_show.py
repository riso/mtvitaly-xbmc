import unittest
from mtvit import MTVItaly

class TestShows(unittest.TestCase):

    def setUp(self):
        self.mtv = MTVItaly('mock_url://')

    def test_list_show(self):
        shows = self.mtv.list_shows()
        self.assertIsNotNone(shows)
        titles = tuple(show[0] for show in shows)
        self.assertIn('Il Testimone', titles)

if __name__ == '__main__':
    unittest.main()
