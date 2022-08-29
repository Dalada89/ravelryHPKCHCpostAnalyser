
base_url = r'https://www.ravelry.com'
group_url = r'/discuss/hp-knitting-crochet-house-cup'


def create_url(ravelry_id, post_id=None, pageonly=False):
    url = '{base}{group}/{id}'

    url = url.format(base=base_url, group=group_url, id=ravelry_id)

    if post_id != None:
        page = int(post_id/25)
        s = page*25+1
        e = page*25+25
        url += '/{s}-{e}'
        if not pageonly:
            url += '#{p}'
        url = url.format(s=s, e=e, p=post_id)

    return url


def test():
    url = create_url(4256123, 1337, pageonly=False)
    print(url)


if __name__ == '__main__':
    test()
