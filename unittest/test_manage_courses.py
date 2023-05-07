from datetime import datetime
import json
from pathlib import Path, PurePath
import unittest
from copy import deepcopy
from unittest.mock import MagicMock
from freezegun import freeze_time
import sys
sys.path.insert(0, str(Path.cwd()))
import manage_courses as mc  # noqa: E402


class TestManageCourses(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(Path('./unittest/test_data/manage_courses_data.json'), 'r') as jsonfile:
            cls.data = json.load(jsonfile)
            cls.data['now'] = datetime.strptime(cls.data['now'], '%Y-%m-%d')
    # def test_add_courses(self):
    #     self.assertEqual(manage_courses.some_function(x), 4)

    # def setUp()

    def test_upload_add_course_file(self):
        mc.nxc.upload_content = MagicMock()

        with freeze_time(self.data['now']):
            mc.upload_add_course_file(courses=[])

        args = mc.nxc.upload_content.call_args_list
        print(args)
        self.assertEqual(args[0][0][1], [self.data['input'][0]])

        # with input
        mc.nxc.upload_content = MagicMock()

        with freeze_time(self.data['now']):
            mc.upload_add_course_file(courses=[self.data['input'][1]])

        args = mc.nxc.upload_content.call_args_list
        self.assertEqual(args[0][0][1], [self.data['input'][1], self.data['input'][0]])

    def test_get_ravelry_id(self):
        self.assertEqual(mc.get_ravelry_id(self.data['input'][0]['url']), self.data['ravelry_id'])
        self.assertEqual(mc.get_ravelry_id(''), -1)
        fake_url = 'https://this.is.a/too/short/id/1234/'
        self.assertEqual(mc.get_ravelry_id(fake_url), -1)
        fake_url = 'https://this.is.a/valid/id/1234567/'
        self.assertEqual(mc.get_ravelry_id(fake_url), 1234567)
        fake_url = 'https://this.url.is/1234567/also/valid/'
        self.assertEqual(mc.get_ravelry_id(fake_url), 1234567)

    def test_is_active(self):
        with freeze_time(self.data['now']):
            test_window1 = []
            for element in self.data['input'][0]['active'][0]:
                test_window1.append(int(datetime.strptime(element, '%Y-%m-%d').timestamp()))
            self.assertEqual(mc.is_active([test_window1]), -1)

            test_window2 = []
            for element in self.data['input'][1]['active'][0]:
                test_window2.append(int(datetime.strptime(element, '%Y-%m-%d').timestamp()))
            self.assertEqual(mc.is_active([test_window2]), 1)

            self.assertEqual(mc.is_active([test_window1, test_window2]), 1)

            self.assertEqual(mc.is_active([test_window1, test_window1]), -1)

    def test_inform_users(self):
        self.assertTrue(True)
        print('\n-unittest for inform_users not implemented yet.')

    def test_update_mode(self):
        self.assertTrue(True)
        print('\n-unittest for update_mode not implemented yet.')

    def test_add_courses(self):
        self.assertTrue(True)
        print('\n-unittest for add_courses not implemented yet.')
        new_courses = deepcopy(self.data['input'])
        mc.nxc.get_file = MagicMock()
        mc.nxc.get_file.return_value = new_courses
        mc.ravelry.get_title = MagicMock()
        mc.ravelry.get_title.side_effect = ['title1']
        mc.courses.insert = MagicMock()
        mc.upload_add_course_file = MagicMock()
        mc.cf.tz_diff = MagicMock()
        mc.cf.tz_diff.return_value = self.data['tz_diff']

        info = mc.add_courses()
        insert_courses = mc.courses.insert.call_args_list

        with open(PurePath('temp1.json'), 'w') as fileobj:
            json.dump(info, fileobj)
        with open(PurePath('temp2.json'), 'w') as fileobj:
            json.dump(insert_courses, fileobj)
        # mc.upload_add_course_file.


if __name__ == '__main__':
    unittest.main()
