import os
import mock
import unittest
from mtvit import MTVItaly

class TestMTV(unittest.TestCase):

    def setUp(self):
        self.mtv = MTVItaly('mock_url://', 3)

    def test_list_show(self):
        shows = self.mtv.list_shows()
        self.assertIsNotNone(shows)
        titles = tuple(show[0] for show in shows)
        self.assertIn('Il Testimone', titles)

    def test_list_seasons(self):
        seasons = self.mtv.list_seasons('il-testimone')
        self.assertIsNotNone(seasons)
        titles = tuple(season[0] for season in seasons)
        self.assertIn('Stagione 1', titles)

    def test_list_seasons_empty(self):
        with self.assertRaises(Exception):
            self.mtv.list_seasons('ballerini-dietro-il-sipario')

    def test_list_episodes(self):
        episodes = self.mtv.list_episodes('il-testimone', 's01')
        self.assertIsNotNone(episodes)
        titles = tuple(episode[0] for episode in episodes)
        self.assertIn('Loco, loco, loco', titles)

    
    @mock.patch('mtvit.urllib')
    def test_quality_selection(self, mock_urllib):
        fn = os.path.join(os.path.dirname(__file__), 'mocks', 'video_qualities_mock.xml')
        mock_urllib.urlopen.return_value = fn
        episode_qualities = self.mtv.list_video_qualities('il-testimone', 's01', 'il-testimone-s01e07')
        self.assertIsNotNone(episode_qualities)
        normalized_qualities = self.mtv.normalize_qualities(episode_qualities)
        self.assertEqual(3, len(normalized_qualities))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
