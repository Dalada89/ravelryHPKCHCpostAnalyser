from datetime import datetime
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock
import json
from copy import deepcopy
sys.path.insert(0, str(Path.cwd()))
from report import inform_users as iu  # noqa: E402


class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(Path('./test_data/inform_users_data.json'), 'r') as jsonfile:
            cls.data = json.load(jsonfile)
            cls.data['data']['name1'][0]['day'] = datetime.strptime(cls.data['data']['name1'][0]['day'], "%Y-%m-%d")
            cls.data['data']['name2'][0]['day'] = datetime.strptime(cls.data['data']['name2'][0]['day'], "%Y-%m-%d")
            cls.data['yesterday']['day'] = datetime.strptime(cls.data['yesterday']['day'], "%Y-%m-%d")

    def test_inform_user(self):
        iu.submissions.get = MagicMock()
        iu.submissions.get.return_value = self.data['submissions']

        iu.cf.get_time_yesterday = MagicMock()
        iu.cf.get_time_yesterday.return_value = (self.data['yesterday']['start'],
                                                 self.data['yesterday']['end'],
                                                 self.data['yesterday']['day'])

        iu.trackers.get = MagicMock()
        iu.trackers.get.side_effect = self.data['trackers']

        iu.sendmail.send = MagicMock()
        iu.sendmail.send.return_value = None

        # Normal behaviour
        iu.inform_user(self.data['courses'])

        args = iu.sendmail.send.call_args_list

        for idx, name in enumerate(self.data['names']):
            tracker = self.data['trackers'][idx][0]
            self.assertEqual(args[idx][0][0], tracker['mail'])
            self.assertEqual(args[idx][0][1], self.data['text'][name][1])
            self.assertEqual(args[idx][0][2], self.data['html'][name][1])

        # No Submissions
        iu.sendmail.send.call_args_list = []
        iu.submissions.get.return_value = []
        iu.trackers.get = MagicMock()
        iu.trackers.get.side_effect = self.data['trackers']
        iu.inform_user(self.data['courses'])
        args = iu.sendmail.send.call_args_list
        for idx, entry in enumerate(args):
            self.assertEqual(entry[0][0], self.data['trackers'][idx][0]['mail'])
            self.assertEqual(entry[0][1], self.data['text']['no_submissions'][idx])
            self.assertEqual(entry[0][2], self.data['html']['no_submissions'][idx])

        # Not tracked
        iu.sendmail.send.call_args_list = []
        iu.trackers.get = MagicMock()
        iu.trackers.get.side_effect = self.data['trackers']
        mod_courses = deepcopy(self.data['courses'])
        mod_courses[0]['tracked_by'] = ''
        iu.inform_user(mod_courses)
        args = iu.sendmail.send.call_args_list

        for call in args:
            self.assertEqual(call, [])

        # Tracker not found
        iu.sendmail.send.call_args_list = []
        iu.trackers.get = MagicMock()
        iu.trackers.get.return_value = []
        self.assertRaises(KeyError, iu.inform_user, self.data['courses'])

    def test_create_text(self):
        for name in self.data['names']:
            text, html = iu.create_text(name, self.data['data'][name])
            self.assertEqual(text, self.data['text'][name][0])
            self.assertEqual(html, self.data['html'][name][0])


if __name__ == '__main__':
    unittest.main()
