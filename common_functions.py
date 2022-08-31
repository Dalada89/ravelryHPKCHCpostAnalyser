import datetime
from pytz import timezone

base_url = r'https://www.ravelry.com'
group_url = r'/discuss/hp-knitting-crochet-house-cup'


def create_url(ravelry_id, post_id=None, pagegiven=None):
    url = '{base}{group}/{id}'

    url = url.format(base=base_url, group=group_url, id=ravelry_id)
    page = None
    if post_id != None:
        page = int(post_id/25) + 1
        if pagegiven != None:
            if page != int(pagegiven):
                msg = 'The post_id {pid} is not on page {given}.'
                raise ValueError(msg.format(given=pagegiven, pid=post_id))
    if pagegiven != None:
        page = int(pagegiven)

    if page != None:
        s = (page - 1) * 25 + 1
        e = (page - 1) * 25 + 25
        url += '/{s}-{e}'
        if post_id != None:
            url += '#{p}'
        url = url.format(s=s, e=e, p=post_id)

    return url


def get_time_yesterday(diff_to_utc=0, day=0):
    """
    get timestamp for yesterday in defined timezone
    """
    if day == 0:
        day = datetime.datetime.today() - datetime.timedelta(days=1)
    else:
        # prüfen was day ist..
        day = day

    start = datetime.datetime(day.year, day.month, day.day, 0, 0, 0) \
        - datetime.timedelta(hours=diff_to_utc)  # .timestamp()
    start_unix = int(start.timestamp())
    end = datetime.datetime(day.year, day.month, day.day, 23, 59, 59) \
        - datetime.timedelta(hours=diff_to_utc)
    end_unix = int(end.timestamp())
    # print(str(start_unix) + " to " + str(end_unix))
    return start_unix, end_unix, day


def tz_diff(date: datetime, target: str, home: str) -> int:
    """
    Returns the difference in hours between timezone1 and timezone2
    for a given date.
    """
    tz1 = timezone(target)
    tz2 = timezone(home)

    diff = (tz1.localize(date) - tz2.localize(date).astimezone(tz1))\
            .seconds/3600
    return int(diff)


def test():
    date = datetime.datetime.now()
    dif = tz_diff(date, 'America/Los_Angeles', 'Europe/Berlin')
    print(dif)
    url = create_url(4256123)
    print(url)


if __name__ == '__main__':
    test()
