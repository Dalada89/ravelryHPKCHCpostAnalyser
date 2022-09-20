from datetime import datetime, timedelta
from pathlib import PurePath
import json
import re
from database import courses
import common_functions as cf


pattern_ravelry_id = '\/([\d]{7})\/'


def get_ravelry_id(url):
    ravelry_id = -1
    match = re.search(pattern_ravelry_id, url)
    if match != None:
        ravelry_id = match.group(1)
    
    return ravelry_id


def get_year(term):
    year = -1
    match = re.search('([\d]{2,4})', term)
    if match != None:
        year = match.group(1)
    if len(year) == 2:
        year = "20" + str(year)
    elif len(year) == 3:
        print('thats not a year: ' + year)
        year = datetime.now().year
    elif len(year) == 4:
        year = str(year)
    return year


def get_start_end(month, year=datetime.now().year):
    """
    This function shall return the start and end timestamps for a month
    """
    year_int = int(year)
    month_int = 0
    try:
        month_int = datetime.strptime(str(month), '%B').month
    except ValueError:
        try:
            month_int = datetime.strptime(str(month), '%b').month
        except ValueError:
            try:
                month_int = int(month)
            except ValueError:
                print('What is that: ' + month)
                return 0, 0
    
    start = datetime(year_int, month_int, 1)
    timezonediff = cf.tz_diff(start, 'America/Los_Angeles', 'Europe/Berlin')
    start = start + timedelta(hours=timezonediff)

    end = datetime(year_int, month_int+1, 1)
    timezonediff = cf.tz_diff(start, 'America/Los_Angeles', 'Europe/Berlin')
    end = end + timedelta(hours=timezonediff)

    # print('{s} - {e}'.format(s=start, e=end))
    start = int(start.timestamp())
    end = int(end.timestamp())

    return start, end


def get_title(url):
    print('getting that title')

    return 'title'


def main():
    with open(PurePath('./add_courses.json'), 'r') as fileobj:
        new_courses = json.load(fileobj)

    for course in new_courses:
        if 'start' not in course and 'end' not in course:
            year = get_year(course['term'])
            course['start'], course['end'] = get_start_end(course['month'], year)
        course['ravelry_id'] = get_ravelry_id(course['url'])
        if course['ravelry_id'] == -1:
            msg = 'Unknown ravelry id in {url}.'.format(url=course['url'])
            continue
        course.pop('url')
        course['mode'] = 1
        course['last_post'] = 0
        # print(course)
        courses.insert(course)


if __name__ == '__main__':
    main()
