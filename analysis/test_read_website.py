from pathlib import Path
import sys
import unittest
import json
sys.path.insert(0, str(Path.cwd()))
from analysis import read_website as rw  # noqa: E402


class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(Path('./test_data/test_side_error.html'), 'r', encoding='utf-8') as html:
            cls.webpage = html.read()
        with open(Path('./test_data/db.json'), 'r') as jsonfile:
            cls.truths = json.load(jsonfile)
        cls.further_data = {
            'ravelry_id': 4153080,
            'url': 'https://www.ravelry.com/discuss/hp-knitting-crochet-house-cup/4153080/151-175',
            'last_post': 151
        }
        cls.extracted, cls.last_post = rw.analysePage(cls.webpage, cls.further_data)

        with open(Path('./test_data/extracted_db.json'), 'w') as jsonfile:
            json.dump(cls.extracted, jsonfile)

    def test_name(self):
        names = []
        for entry in self.extracted:
            for truth in self.truths:
                if entry['name'] == truth['name']:
                    names.append(entry['name'])
                    break
        self.assertEqual(len(names), len(self.truths))

        names = []
        for truth in self.truths:
            for entry in self.extracted:
                if entry['name'] == truth['name']:
                    names.append(entry['name'])
                    break
        self.assertEqual(len(names), len(self.extracted))

    def test_post_data(self):
        for entry in self.extracted:
            self.assertEqual(entry['ravelry_id'], self.further_data['ravelry_id'])
            for truth in self.truths:
                if entry['name'] == truth['name']:
                    self.assertEqual(entry['post_id'], truth['post_id'])
                    self.assertEqual(entry['house'], truth['house'])
                    self.assertEqual(entry['project'], truth['project'])
                    self.assertEqual(entry['points'], truth['points'])
                    self.assertEqual(entry['status'], truth['status'])
                    break

    def test_date(self):
        for entry in self.extracted:
            for truth in self.truths:
                if entry['name'] == truth['name']:
                    # I really don't know why I have to add 6h to the date. When I get the page with python, it has always an offset of 6h.
                    # Propably it depends on the timezone ?!?!
                    # The truth must be the real unixtimestamp calculated by an online converter
                    self.assertEqual(entry['date'], truth['date'] + 6*60*60)
                    self.assertEqual(type(entry['date']), int)
                    break


if __name__ == '__main__':
    unittest.main()
