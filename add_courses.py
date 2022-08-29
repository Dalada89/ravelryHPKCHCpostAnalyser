from datetime import datetime
from pathlib import PurePath
import json
import re
from database import courses


pattern_ravelry_id = '\/([\d]{7})\/'


def get_ravelry_id(url):
    ravelry_id = -1
    match = re.search(pattern_ravelry_id, url)
    if match != None:
        ravelry_id = match.group(1)
    
    return ravelry_id


def get_title(url):
    print('getting that title')

    return 'title'


def main():
    with open(PurePath('./add_courses.json'), 'r') as fileobj:
        new_courses = json.load(fileobj)

    for course in new_courses:
        course['ravelry_id'] = get_ravelry_id(course['url'])
        if course['ravelry_id'] == -1:
            msg = 'Unknown ravelry id in {url}.'.format(url=course['url'])
            continue
        course.pop('url')
        course['active'] = 1
        course['last_post'] = 0

        courses.insert(course)


if __name__ == '__main__':
    main()
