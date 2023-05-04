from datetime import datetime, timedelta
from pytz import timezone

base_url = r'https://www.ravelry.com'
group_url = r'/discuss/hp-knitting-crochet-house-cup'


def create_url(ravelry_id, post_id=None, pagegiven=None):
    url = '{base}{group}/{id}'

    url = url.format(base=base_url, group=group_url, id=ravelry_id)
    page = None
    if post_id is not None:
        page = int((post_id-1)/25) + 1
        if pagegiven is not None:
            if page != int(pagegiven):
                msg = 'The post_id {pid} is not on page {given}.'
                raise ValueError(msg.format(given=pagegiven, pid=post_id))
    if pagegiven is not None:
        page = int(pagegiven)

    if page is not None:
        s = (page - 1) * 25 + 1
        e = (page - 1) * 25 + 25
        url += '/{s}-{e}'
        if post_id is not None:
            url += '#{p}'
        url = url.format(s=s, e=e, p=post_id)

    return url


def get_time_yesterday(diff_to_utc: int = 0):
    """
    get timestamp for yesterday in defined timezone
    """
    day = datetime.today() - timedelta(days=1)
    start, end = get_start_end(day, diff_to_utc=diff_to_utc)

    return start, end, day


def get_start_end(day: datetime, diff_to_utc: int = 0):
    start = datetime(day.year, day.month, day.day, 0, 0, 0) \
        - timedelta(hours=diff_to_utc)  # .timestamp()
    start_unix = int(start.timestamp())
    end = datetime(day.year, day.month, day.day, 23, 59, 59) \
        - timedelta(hours=diff_to_utc)
    end_unix = int(end.timestamp())
    # print(str(start_unix) + " to " + str(end_unix))
    return start_unix, end_unix


def tz_diff(date: datetime, target: str, home: str) -> int:
    """
    Returns the difference in hours between timezone1 and timezone2
    for a given date.
    """
    tz1 = timezone(target)
    tz2 = timezone(home)

    diff = (tz1.localize(date) - tz2.localize(date).astimezone(tz1))\
            .seconds/3600  # noqa: E127
    return int(diff)


def get_last_date_of_month(year, month):
    """
    Return the last date of the month.
    Args:
        year (int): Year, i.e. 2022
        month (int): Month, i.e. 1 for January

    Returns:
        date (datetime): Last date of the current month
    """

    if month == 12:
        last_date = datetime(year, month, 31)
    else:
        last_date = datetime(year, month + 1, 1) + timedelta(days=-1)

    return last_date


def test():
    date = datetime.datetime.now()
    dif = tz_diff(date, 'America/Los_Angeles', 'Europe/Berlin')
    print(dif)
    url = create_url(4256123, post_id=1)
    print(url)


if __name__ == '__main__':
    test()
