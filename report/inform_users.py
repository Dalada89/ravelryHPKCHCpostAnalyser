import locale
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path.cwd()))
from database import trackers, courses, submissions  # noqa: E402
from services import sendmail  # noqa: E402
import common_functions as cf  # noqa: E402


def inform_user(class_pages):
    start, end, day = cf.get_time_yesterday(-9)
    # start = 1658707200
    # end = start + 24*60*60
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
            posts = submissions.get(filter=filter, start=start, end=end)
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
            raise Exception(msg)
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


def test():
    class_pages = courses.get(filter={'mode': 1})
    inform_user(class_pages)


if __name__ == '__main__':
    test()
