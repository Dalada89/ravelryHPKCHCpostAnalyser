import unittest
from pathlib import Path
import json
import read_website as rw


class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(r'.\test_data\test_side_error.html', 'r', encoding='utf-8') as html:
            cls.webpage = html.read()
        with open(r'.\test_data\db.json', 'r') as jsonfile:
            cls.truths = json.load(jsonfile)
        cls.further_data = {
            'class_id': 4153080,
            'url': 'https://www.ravelry.com/discuss/hp-knitting-crochet-house-cup/4153080/151-175'
        }
        cls.extracted = rw.analysePage(cls.webpage, cls.further_data)

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
            self.assertEqual(entry['class_id'], self.further_data['class_id'])
            for truth in self.truths:
                if entry['name'] == truth['name']:
                    self.assertEqual(entry['post_id'], truth['post_id'])
                    self.assertEqual(entry['house'], truth['house'])
                    self.assertEqual(entry['project'], truth['project'])
                    self.assertEqual(entry['verb'], truth['verb'])
                    self.assertEqual(entry['loved'], truth['loved'])
                    break

    def test_date(self):
        for entry in self.extracted:
            for truth in self.truths:
                if entry['name'] == truth['name']:
                    # I really don't know why I have to add 6h to the date. When I get the page with python, it has always an offset of 6h.
                    # Propably it depends on the timezone ?!?!
                    self.assertEqual(entry['date'], truth['date'] + 6*60*60)
                    self.assertEqual(type(entry['date']), int)
                    break

    def test_url(self):
        for entry in self.extracted:
            for truth in self.truths:
                if entry['name'] == truth['name']:
                    self.assertEqual(entry['url'], truth['url'])
                    self.assertIn(self.further_data['url'], truth['url'])
                    break


if __name__ == '__main__':
    unittest.main()
