from datetime import datetime, timedelta
import locale
import re
from database import courses, trackers
import common_functions as cf
from services import ravelry, sendmail, nxc


pattern_ravelry_id = r'\/([\d]{7})\/'
date_pattern = '%B %-d, %Y'
nxc_path_add_courses = 'courses/add/add_courses.json'


def get_ravelry_id(url):
    ravelry_id = -1
    match = re.search(pattern_ravelry_id, url)
    if match is not None:
        ravelry_id = match.group(1)

    return int(ravelry_id)


def upload_add_course_file(courses=[]):

    now = datetime.now()

    if now.month in [1, 2, 3]:
        term = 'W' + str(now.year)
    elif now.month in [4, 5, 6, 7]:
        term = 'S' + str(now.year)
    elif now.month in [8, 9, 10, 11]:
        term = 'F' + str(now.year)
    elif now.month in [12]:
        term = 'W' + str(now.year + 1)
    # Mark as Blueprint: Course ID 1337421
    blue_print = {
        "url": "https://www.ravelry.com/discuss/hp-knitting-crochet-house-cup/1337421/",
        "term": term,
        "active": [["2022-10-01", "2022-10-31"]],
        "type": "class",
        "tracked_by": "nickname",
        "base_points": 15
    }

    courses.append(blue_print)

    nxc.upload_content(nxc_path_add_courses, courses)


def add_courses():

    new_courses = nxc.get_file(nxc_path_add_courses)

    info = {}
    to_remove = []
    for course in new_courses:
        course['ravelry_id'] = get_ravelry_id(course['url'])
        if course['ravelry_id'] == -1:
            msg = 'Unknown ravelry id in {url}.'.format(url=course['url'])
            print(msg)
            continue
        elif course['ravelry_id'] == 1337421:  # Blueprint entry
            to_remove.append(course)
            continue
        ts_active_list = []
        for el in course['active']:
            if len(el) != 2:
                msg = "[manage_courses.add_courses] The field 'active' has an "
                msg += "element {item} with more or less than two dates."
                print(msg)
                continue
            active = []
            for date in el:
                try:
                    temp = datetime.strptime(date, '%Y-%m-%d')
                    timezonediff = cf.tz_diff(temp, 'UTC', 'Europe/Berlin')
                    temp = temp + timedelta(hours=timezonediff)
                    active.append(int(temp.timestamp()))
                except TypeError:
                    msg = "[manage_courses.add_courses] The field 'active' has a "
                    msg += "date {item} that does not match the pattern '%Y-%m-%d'."
                    print(msg)
                    continue
            active.sort()
            ts_active_list.append(active)
        course['active'] = ts_active_list
        course['title'] = ravelry.get_title(course['url'], out=False)
        if course['title'] is None:
            course['title'] = course.pop('url')
        else:
            course.pop('url')

        course['mode'] = 0
        course['last_post'] = 0
        course['type'] = course['type'].lower()
        courses.insert(course)

        if course['tracked_by'] != '':
            tracked_by = course['tracked_by'].split(';')
            for truker in tracked_by:
                if truker not in info:
                    info[truker] = []

                info[truker].append({
                    'ravelry_id': course['ravelry_id'],
                    'title': course['title'],
                    'start': course['active'][0][0]
                })
        to_remove.append(course)

    for el in to_remove:
        new_courses.remove(el)

    upload_add_course_file(new_courses)

    return info


def update_mode():
    """
    This function shall update the modus of all courses.
    modes:
        - 0: course not started
        - 1: active, submissions possible
        - 2: waiting for points, submissions not possible
        - 3: closed, points graded
    """

    db_courses = courses.get(filter={'mode': 0})
    db_courses.extend(courses.get(filter={'mode': 1}))
    info = {}
    for course in db_courses:
        changed = False
        if course['mode'] == 0:
            if is_active(course['active']) == 1:
                course['mode'] = 1
                changed = True
        elif course['mode'] == 1:
            if is_active(course['active']) == -1:
                course['mode'] = 2
                changed = True
            elif is_active(course['active']) == 0:
                course['mode'] = 0
                changed = True

        if changed:
            courses.update(course)
            if course['tracked_by'] != '':
                tracked_by = course['tracked_by'].split(';')
                for truker in tracked_by:
                    if truker not in info:
                        info[truker] = []

                    info[truker].append({
                        'ravelry_id': course['ravelry_id'],
                        'title': course['title'],
                        'mode': course['mode']
                    })
    return info


def is_active(time_windows: list) -> bool:
    """
    This function shall check if now is in a time_window in the list.
    """
    now = int(datetime.now().timestamp())
    active = 0
    max_date = 0
    for window in time_windows:
        if max_date < max(window):
            max_date = max(window)
        if min(window) < now and max(window) > now:
            active = 1

    if max_date < now:
        active = -1

    return active


def inform_users(info):
    """
    This function shall inform users of changes via mail
    """
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    new_info = {}
    # print(info)
    for key in info:
        for tracker in info[key]:
            if tracker not in new_info:
                new_info[tracker] = {}
            if key not in new_info[tracker]:
                new_info[tracker][key] = []

            for entry in info[key][tracker]:
                new_info[tracker][key].append(entry)
    # print(new_info)
    for tracker in new_info:
        tracker_info = trackers.get(filter={'nickname': tracker})
        print(tracker_info)
        if tracker_info != []:
            tracker_info = tracker_info[0]
            html = '<html><body><p>Hello {name},<br><br>'.format(name=tracker_info['name'])
            text = 'Hello {name},\n\n'.format(name=tracker_info['name'])
            html += 'There are some news for HPKCHC tracking.<br><br>'
            text += 'There are some news for HPKCHC tracking.\n\n'

            if 'new_courses' in new_info[tracker]:
                if new_info[tracker]['new_courses'] != []:
                    html += 'You have been added as tracker for the following courses:<br>'
                    text += 'You have been added as tracker for the following courses:\n'
                    html += '<ul>'
                    for entry in new_info[tracker]['new_courses']:
                        url = cf.create_url(entry['ravelry_id'])
                        start = datetime.fromtimestamp(entry['start'])
                        html += '<li><a href="{url}">{title}</a><br>'.format(url=url, title=entry['title'])
                        text += '- {title}, {url}\n'.format(url=url, title=entry['title'])
                        html += '<i>Start {start}</i></li>'.format(start=start.strftime(date_pattern))
                        text += '  Start {start}\n'.format(start=start.strftime(date_pattern))
                    html += '</ul>'
                    text += '\n'

            if 'changed' in new_info[tracker]:
                if new_info[tracker]['changed'] != []:
                    html += 'The following course have changed:<br>'
                    text += 'The following course have changed:\n'
                    html += '<ul>'
                    for entry in new_info[tracker]['changed']:
                        url = cf.create_url(entry['ravelry_id'])
                        if entry['mode'] == 0:
                            mode = 'is now inactive'
                        elif entry['mode'] == 1:
                            mode = 'is active'
                        elif entry['mode'] == 2:
                            mode = 'waiting for points'
                        elif entry['mode'] == 3:
                            mode = 'closed'
                        html += '<li><a href="{url}">{title}</a><br>'.format(url=url, title=entry['title'])
                        text += '- {title}, {url}\n'.format(url=url, title=entry['title'])
                        html += '<i>{mod}</i></li>'.format(mod=mode)
                        text += '  {mod}\n'.format(mod=mode)
                    html += '</ul>'
                    text += '\n'

            html += "<br>Bye<br>Your Ravenclaw Tracker</p></body></html>"
            text += "Bye\nYour Ravenclaw Tracker"

            sendmail.send(tracker_info['mail'], text, html)


def main():
    info_to_send = {}
    info_to_send['new_courses'] = add_courses()
    info_to_send['changed'] = update_mode()
    inform_users(info_to_send)


if __name__ == '__main__':
    main()
