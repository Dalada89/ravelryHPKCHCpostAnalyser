import json
from datetime import datetime
import pytz
import pandas as pd
from pathlib import Path, PurePath
import sys
sys.path.insert(0, str(Path.cwd()))
from services import nxc  # noqa: E402
from database import submissions, courses  # noqa: E402
import common_functions as cf  # noqa: E402
from report import diagrams  # noqa: E402

tz = 'UTC'
date_pattern = '%b %-d, %Y %H:%M UTC'
with open('listOfHouses.json', 'r') as file:
    listOfHouses = json.load(file)


def prepare_path(course):
    """
    This function shall prepare a name to be used as a folder name
    """
    name = course['title']
    with open(PurePath('./report/paths.json'), 'r') as fileobj:
        paths = json.load(fileobj)
    replace_chars = {
        ':': '',
        ' ': '_',
        '/': '_'
    }

    for char in replace_chars:
        name = name.replace(char, replace_chars[char])

    path = Path(PurePath(paths['report'][course['type']]).joinpath(course['term'], name))
    nxc.make_dir(path)

    return path


def report_classes():
    """
    This function shall create a report for classes and save it into the nextcloud folder
    """
    active_classes = courses.get(filter={'mode': 1, 'type': 'class'})

    for aclass in active_classes:
        data = submissions.get(filter={'ravelry_id': aclass['ravelry_id']})
        directory = prepare_path(aclass)
        if data:
            diagrams.plot_timeline(data, aclass, directory)

        report = '# {title}\n\n'.format(title=aclass['title'])
        now = datetime.now().astimezone(pytz.timezone(tz))
        report += 'Updated: {now}\n\n'.format(now=now.strftime(date_pattern))
        url_first_page = cf.create_url(aclass['ravelry_id'])
        url_last_page = cf.create_url(aclass['ravelry_id'], post_id=aclass['last_post'])
        url_last_page = url_last_page[0:-(len(str(aclass['last_post']))+1)]
        report += '[First Page]({url_f}) - [Last Page]({url_l})\n\n'.format(url_f=url_first_page, url_l=url_last_page)

        if data:
            report += '![timeline](./timeline.png)\n\n'
        else:
            report += '(As soon as data is available there will be a timeline here)'

        report += '## Timeline Submissions\n\n'
        report += 'In total: {n} submissions\n\n'.format(n=len(data))
        report += '|No.|Name|House|Post|Date|\n'
        report += '|---|----|-----|----|----|\n'
        data = sorted(data, key=lambda item: item['date'])
        df = pd.DataFrame(data)
        cur_day = 0
        for idx, row in enumerate(data):
            date = datetime.fromtimestamp(row['date']).astimezone(pytz.timezone(tz))
            if date.day > cur_day:
                cur_day = date.day
                report += '| | |**{date}**| | |\n'.format(date=date.strftime('%B %-d, %Y'))
            url = cf.create_url(row['ravelry_id'], post_id=row['post_id'])
            report += '|{i}|{n}|{h}|[{pi}]({u})|{d}|\n'.format(i=idx+1, n=row['name'],
                                                               h=row['house'], pi=row['post_id'],
                                                               u=url, d=date.strftime(date_pattern))

        report += '\n\n'
        report += '## Sort by houses\n\n'
        for house in listOfHouses:
            report += '### {house}\n\n'.format(house=house)
            filt = [d for d in data if d['house'] == house]
            filt = sorted(filt, key=lambda item: item['name'].lower())
            report += 'In total: {n} submissions\n\n'.format(n=len(filt))
            report += '|No.|Name|Post|Date|\n'
            report += '|---|----|----|----|\n'
            for idx, row in enumerate(filt):
                date = datetime.fromtimestamp(row['date']).astimezone(pytz.timezone(tz))
                url = cf.create_url(row['ravelry_id'], post_id=row['post_id'])
                report += '|{i}|{n}|[{pi}]({u})|{d}|\n'.format(i=idx+1, n=row['name'],
                                                               pi=row['post_id'],
                                                               u=url, d=date.strftime(date_pattern))

        filename = 'report.md'

        with open(nxc.temp_dir.joinpath(filename), 'w') as fileobj:
            fileobj.write(report)
        nxc.upload_file(nxc.temp_dir.joinpath(filename), directory, del_file=True)

        filename = 'rawdata.csv'
        df.to_csv(nxc.temp_dir.joinpath(filename))
        nxc.upload_file(nxc.temp_dir.joinpath(filename), directory, del_file=True)

        print('Uploaded class report for {cls} to nextcloud tracking.'.format(cls=aclass['title']))


def create_reports():
    """
    This function shall trigger all reports for nextcloud
    """
    report_classes()


def main():
    """
    Main Program
    """
    create_reports()


if __name__ == '__main__':
    main()
