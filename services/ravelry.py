import json
import requests
from bs4 import BeautifulSoup as bs
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import common_functions as cf  # noqa: E402


session = None
token = None


def get_session():
    global session
    global token
    if session is None:
        with open('credentials.json', 'r') as file:
            credentials = json.load(file)

        session = requests.Session()
        site = session.get(cf.base_url + r'/account/login')
        bs_content = bs(site.content, 'html.parser')
        token = bs_content.find('input', {'name': 'authenticity_token'})['value']
        login_data = {
            'user[login]': credentials['ravelry']['username'],
            'user[password]': credentials['ravelry']['password'],
            'authenticity_token': token,
            'origin': 'splash',
            'return_to': ''}

        session.post(cf.base_url + r'/account/login', login_data)
        home_page = session.get(cf.base_url)
        bs_content = bs(home_page.content, 'html.parser')
        token = bs_content.find('meta', {'name': 'authenticity-token'})['content']
        print('logged into ravelry')


def logout():
    global session
    global token
    if session is not None:
        session.post(cf.base_url + r'/account/logout', {'authenticity_token': token})

        session = None

    return session is None


def get_page(url):
    global session
    if session is None:
        get_session()

    site = session.get(url)
    soup = bs(site.content, 'html.parser')

    return soup


def get_title(url, out=True):
    soup = get_page(url)

    item = soup.find_all(class_="topic_heading rsp_hidden")
    if item != []:
        title = item[0].getText()
        title = title.rstrip()
    else:
        title = None

    if out:
        logout()

    return title


def main():
    url = 'https://www.ravelry.com/discuss/hp-knitting-crochet-house-cup/4215918/1-25'
    site = get_title(url)

    print('>' + site + '<')


if __name__ == '__main__':
    logout()
    main()
