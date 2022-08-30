
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


def test():
    url = create_url(4256123)
    print(url)


if __name__ == '__main__':
    test()
