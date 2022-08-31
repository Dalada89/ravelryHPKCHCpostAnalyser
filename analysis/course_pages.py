import json
from requests import Session
from bs4 import BeautifulSoup as bs
import common_functions as cf
from analysis import read_website
from database import courses


def analyse_game_pages(class_pages):
    with open('credentials.json', 'r') as file:
        credentials = json.load(file)

    with Session() as s:
        site = s.get(cf.base_url + r'/account/login')
        bs_content = bs(site.content, 'html.parser')
        token = bs_content.find('input', {'name': 'authenticity_token'})['value']
        login_data = {
            'user[login]': credentials['ravelry']['username'],
            'user[password]': credentials['ravelry']['password'],
            'authenticity_token': token,
            'origin': 'splash',
            'return_to': ''}

        s.post(cf.base_url + r'/account/login', login_data)
        home_page = s.get(cf.base_url)
        bs_content = bs(home_page.content, 'html.parser')
        token = bs_content.find('meta', {'name': 'authenticity-token'})['content']

        database = []
        for page in class_pages:
            start_page = int(page['last_post']/25)
            site = s.get(cf.create_url(page['ravelry_id']))
            soup = bs(site.content, 'html.parser')
            count_pages_soup = soup.find_all(class_='page_bar__page')
            count_pages = 1
            if len(count_pages_soup) != 0:
                count_pages = int(count_pages_soup[-1].getText())
                print(page['title'] + ' hat ' + count_pages_soup[-1].getText() + ' Seiten.')
            else:
                print(page['title'] + ' hat eine Seite.')
            for i in range(0, count_pages - start_page): ########## Hier stimmt noch was nicht WEITER MACHEN
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
                # print(further_data)
                site = s.get(url)
                result, last_post = read_website.analysePage(site.content, further_data)
                database.extend(result)
                page['last_post'] = int(last_post)
            courses.update(page)
                # print(base_url + group_url + r'/' + page['id'] + '/' + str(i*25+1) + '-' + str(i*25+25))
        # run program

        s.post(cf.base_url + r'/account/logout', {'authenticity_token': token})

    return database
