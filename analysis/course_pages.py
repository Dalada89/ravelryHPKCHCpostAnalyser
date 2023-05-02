from services import ravelry
import common_functions as cf
from analysis import read_website
from database import courses


def analyse_game_pages(class_pages):

    database = []
    for page in class_pages:
        start_page = int(page['last_post']/25)
        soup = ravelry.get_page(cf.create_url(page['ravelry_id']))
        count_pages_soup = soup.find_all(class_='page_bar__page')
        count_pages = 1
        submissons = 0
        first_post = page['last_post']
        if len(count_pages_soup) != 0:
            count_pages = int(count_pages_soup[-1].getText())
        for i in range(0, count_pages - start_page):
            if i == 0:
                pageside = int(page['last_post']/25) + 1
                start_with_post = page['last_post'] + 1
            else:
                pageside += 1
                start_with_post = (pageside - 1) * 25 + 1
            url = cf.create_url(page['ravelry_id'], pagegiven=pageside)
            further_data = {
                'ravelry_id': page['ravelry_id'],
                'url': url,
                'last_post': start_with_post
            }
            site = ravelry.get_page(url)
            result, last_post = read_website.analysePage(site, further_data)
            submissons += len(result)
            database.extend(result)
            page['last_post'] = int(last_post)
        courses.update(page)
        analysed_posts = page['last_post'] - first_post
        msg = 'Course {title} has {nPost} new posts with {sm} submissions.'
        msg = msg.format(title=page['title'], nPost=analysed_posts, sm=submissons)
        print(msg)

    ravelry.logout()

    return database
