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
            cls.result = json.load(jsonfile)

    def test_read(self):
        further_data = {
            'class_id': 4153080,
            'url': 'https://www.ravelry.com/discuss/hp-knitting-crochet-house-cup/4153080/151-17'
        }
        db = rw.analysePage(self.webpage, further_data)

        with open(Path('./test_data/extracted_db.json'), 'w') as jsonfile:
            json.dump(db, jsonfile)

        for entry in db:
            self.assertIn(entry, self.result)

        for entry in self.result:
            self.assertIn(entry, db)


if __name__ == '__main__':
    unittest.main()
