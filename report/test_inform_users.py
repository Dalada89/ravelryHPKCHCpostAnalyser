from datetime import datetime
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock
import json
sys.path.insert(0, str(Path.cwd()))
from report import inform_users as iu  # noqa: E402


class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(Path('./test_data/courses.json'), 'r') as jsonfile:
            cls.courses = json.load(jsonfile)
        with open(Path('./test_data/trackers.json'), 'r') as jsonfile:
            cls.trackers = json.load(jsonfile)
        with open(Path('./test_data/submissions.json'), 'r') as jsonfile:
            cls.submissons = json.load(jsonfile)
        with open(Path('./test_data/inform_users_data.json'), 'r') as jsonfile:
            cls.data = json.load(jsonfile)
            cls.data['data']['name1'][0]['day'] = datetime.strptime(cls.data['data']['name1'][0]['day'], "%Y-%m-%d")
            cls.data['data']['name2'][0]['day'] = datetime.strptime(cls.data['data']['name2'][0]['day'], "%Y-%m-%d")
            cls.data['yesterday']['day'] = datetime.strptime(cls.data['yesterday']['day'], "%Y-%m-%d")

    def test_inform_user(self):
        iu.submissions.get = MagicMock()
        iu.submissions.get.return_value = self.submissons

        iu.cf.get_time_yesterday = MagicMock()
        iu.cf.get_time_yesterday.return_value = (self.data['yesterday']['start'],
                                                 self.data['yesterday']['end'],
                                                 self.data['yesterday']['day'])

        iu.trackers.get = MagicMock()
        iu.trackers.get.side_effect = self.trackers

        iu.sendmail.send = MagicMock()
        iu.sendmail.send.return_value = None

        iu.inform_user(self.courses)

        args = iu.sendmail.send.call_args_list

        for idx, name in enumerate(self.data['names']):
            tracker = self.trackers[idx][0]
            self.assertEqual(args[idx][0][0], tracker['mail'])
            self.assertEqual(args[idx][0][1], self.data['text'][name][1])
            self.assertEqual(args[idx][0][2], self.data['html'][name][1])

    def test_create_text(self):
        for name in self.data['names']:
            text, html = iu.create_text(name, self.data['data'][name])
            self.assertEqual(text, self.data['text'][name][0])
            self.assertEqual(html, self.data['html'][name][0])


if __name__ == '__main__':
    unittest.main()
