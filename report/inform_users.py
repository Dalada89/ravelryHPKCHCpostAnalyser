import locale
from pathlib import Path
from datetime import datetime
import sys
import json
sys.path.insert(0, str(Path.cwd()))
from database import trackers, submissions, courses  # noqa: E402
from services import sendmail  # noqa: E402
import common_functions as cf  # noqa: E402


def inform_user(class_pages, mycursor=None):
    start, end, day = cf.get_time_yesterday(-9)
    prepare_data(class_pages, start, end, day, mycursor)


def prepare_data(class_pages, start, end, day, mycursor=None):
    with open('listOfHouses.json', 'r') as file:
        listOfHouses = json.load(file)

    data = {}

    for clss in class_pages:
        tracked_by = clss['tracked_by'].split(';')

        for truker in tracked_by:
            if truker == '':
                continue
            if truker.lower() not in data:
                data[truker.lower()] = []

            filter = {
                'ravelry_id': clss['ravelry_id']
            }
            if mycursor is None:
                posts = submissions.get(filter=filter, start=start, end=end)
            else:
                posts = submissions.get(filter=filter, start=start, end=end, mycursor=mycursor)
            posts = sorted(posts, key=lambda x: x['post_id'])

            element = {
                'title': clss['title'],
                'posts': posts,
                'day': day,
                'ranking': {}
            }

            for house in listOfHouses:
                element['ranking'][house] = 0

            for post in posts:
                element['ranking'][post['house']] += 1

            data[truker.lower()].append(element)

    for key in data:
        tracker = trackers.get(filter={'nickname': key})
        if len(tracker) != 1:
            msg = 'Something went wrong.. No or to many trackers for nickname {n} found in the database.'
            msg.format(n=key)
            raise KeyError(msg)
        else:
            tracker = tracker[0]
        text, html = create_text(tracker['name'], data[key])

        sendmail.send(tracker['mail'], text, html)


def create_text(name, results):
    # Create the plain-text and HTML version of your message
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    date_pattern = '%B %-d, %Y'
    text = "Hi {tracka},\n\n".format(tracka=name)
    html = "<html><body><p>Hi {tracka},<br><br>".format(tracka=name)
    text = text + "Here are your daily ravelry results:\n\n"
    html = html + "Here are your daily ravelry results:<br><br>"

    for res in results:
        text += "{date} - {course}\n".format(date=res['day'].strftime(date_pattern), course=res['title'])
        html += "<h2>{date} - {course}</h2><br>".format(date=res['day'].strftime(date_pattern), course=res['title'])

        html += "<ol><li>Houses:<ul>"
        for key in res['ranking']:
            text += "{house}: {n}\n".format(house=key, n=res['ranking'][key])
            html += "<li>{house}: {n}</li>".format(house=key, n=res['ranking'][key])
        html += "</ul><li>Posts:<ul>"
        for post in res['posts']:
            url = cf.create_url(post['ravelry_id'], post_id=post['post_id'])
            html += '<li><a href="{url}">{pid}</a> - {name} (<em>{house}</em>),</li>'.format(url=url,
                                                                                             pid=post['post_id'],
                                                                                             name=post['name'],
                                                                                             house=post['house'])
        html += "</ul></li></ol>"
        text += "\n"
        html += "<br>"

    text += "\nBye\nYour Ravenclaw Tracker"
    html += "<br>Bye<br>Your Ravenclaw Tracker</p></body></html>"

    return text, html


def main():
    fail = False
    if len(sys.argv) == 1:
        msg = 'Please give a date argument like %Y-%m-%d. Example: "2023-05-04"'
        fail = True
    day_str = sys.argv[1]
    try:
        date = datetime.strptime(day_str, "%Y-%m-%d")
    except ValueError:
        msg = 'The given date {date} does not match the format %Y-%m-%d.'.format(date=day_str)
        fail = True

    if fail:
        print(msg)
        return None

    # print(date.astimezone().tzinfo)
    class_pages = courses.get(filter={'mode': 1})
    diff = cf.tz_diff(date, 'America/Los_Angeles', 'Europe/Berlin')
    start, end = cf.get_start_end(date, diff_to_utc=diff*-1)
    prepare_data(class_pages=class_pages, start=start, end=end, day=date)
    # print(datetime.now(timezone.utc).astimezone().tzinfo)


if __name__ == '__main__':
    main()
