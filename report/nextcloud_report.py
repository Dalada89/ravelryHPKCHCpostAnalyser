import json
from datetime import datetime
from pathlib import Path, PurePath
import sys
sys.path.insert(0, str(Path.cwd()))
from database import submissions, courses  # noqa: E402
import common_functions as cf  # noqa: E402


date_pattern = '%B %-d, %Y %H:%M UTC'


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

    path = Path(PurePath(paths['report'][course['type']]).joinpath(name))
    if not path.is_dir():
        path.mkdir()

    return path


def report_classes():
    """
    This function shall create a report for classes and save it into the nextcloud folder
    """
    active_classes = courses.get(filter={'mode': 1, 'type': 'class'})

    for aclass in active_classes:
        data = submissions.get(filter={'ravelry_id': aclass['ravelry_id']})
        directory = prepare_path(aclass)

        report = '# {title}\n\n'.format(title=aclass['title'])
        now = datetime.now()
        report += 'Updated: {now}\n\n'.format(now=now.strftime(date_pattern))

        report += 'here is an image\n\n'

        report += '## Timeline Submissions\n\n'
        report += 'In total: {n} submissions\n\n'.format(n=len(data))
        report += '|No.|Name|House|Post|Date|\n'
        report += '|---|----|-----|----|----|\n'
        data = sorted(data, key=lambda item: item['date'])
        cur_day = 0
        for idx, row in enumerate(data):
            date = datetime.fromtimestamp(row['date'])
            if date.day > cur_day:
                cur_day = date.day
                report += '| | |**{date}**| | |\n'.format(date=date.strftime('%B %-d, %Y'))
            url = cf.create_url(row['ravelry_id'], post_id=row['post_id'])
            report += '|{i}|{n}|{h}|[{pi}]({u})|{d}|\n'.format(i=idx+1, n=row['name'],
                                                               h=row['house'], pi=row['post_id'],
                                                               u=url, d=date.strftime(date_pattern))

        report += '\n'
        directory = directory.joinpath('readme.md')
        with open(directory, 'w') as fileobj:
            fileobj.write(report)


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
