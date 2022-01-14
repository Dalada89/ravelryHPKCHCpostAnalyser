import json
import datetime
from requests import Session
from bs4 import BeautifulSoup as bs
import read_website
import database.posts as dbposts
import sendmail

base_url = r'https://www.ravelry.com'
group_url = r'/discuss/hp-knitting-crochet-house-cup'


def analyse_game_pages():
    with open('credentials.json', 'r') as file:
        credentials = json.load(file)

    with open('hp_classes.json', 'r') as file:
        class_pages = json.load(file)

    with Session() as s:
        site = s.get(base_url + r'/account/login')
        bs_content = bs(site.content, 'html.parser')
        token = bs_content.find('input', {'name': 'authenticity_token'})['value']
        login_data = {
            'user[login]': credentials['ravelry']['username'],
            'user[password]': credentials['ravelry']['password'],
            'authenticity_token': token,
            'origin': 'splash',
            'return_to': ''}

        s.post(base_url + r'/account/login', login_data)
        home_page = s.get(base_url)
        bs_content = bs(home_page.content, 'html.parser')
        token = bs_content.find('meta', {'name': 'authenticity-token'})['content']

        database = []
        for page in class_pages:
            site = s.get(base_url + group_url + r'/' + page['id'])
            soup = bs(site.content, 'html.parser')
            count_pages_soup = soup.find_all(class_='page_bar__page')
            count_pages = 1
            if len(count_pages_soup) != 0:
                count_pages = int(count_pages_soup[-1].getText())
                print(page['name'] + ' hat ' + count_pages_soup[-1].getText() + ' Seiten.')
            else:
                print(page['name'] + ' hat eine Seite.')
            for i in range(0, count_pages):
                further_data = {
                    'class_id': page['id'],
                    'url': base_url + group_url + r'/' + page['id'] + '/' + str(i*25+1) + '-' + str(i*25+25)
                }
                site = s.get(base_url + group_url + r'/' + page['id'] + '/' + str(i*25+1) + '-' + str(i*25+25))
                result = read_website.analysePage(site.content, further_data)
                database.extend(result)
                # print(base_url + group_url + r'/' + page['id'] + '/' + str(i*25+1) + '-' + str(i*25+25))
        # run program

        s.post(base_url + r'/account/logout', {'authenticity_token': token})

    return database


def inform_user():
    start, end, day = get_time(-9)
    with open('listOfHouses.json', 'r') as file:
        listOfHouses = json.load(file)

    with open('hp_classes.json', 'r') as file:
        class_pages = json.load(file)
    class_list = []
    for clss in class_pages:
        class_list.append(clss['id'])

    posts = dbposts.get_multi(class_list, start, end)
    results = []
    for clss in class_pages:
        element = {}
        element['class'] = clss
        element['day'] = day
        element['houses'] = {}
        for house in listOfHouses:
            element['houses'][house] = 0
        element['posts'] = []

        # print(len(posts))
        for post in posts:
            # print(str(type(clss['id'])) + " == " + str(type(post['class_id'])))
            if int(clss['id']) == int(post['class_id']):
                element['houses'][post['house']] += 1
                element['posts'].append(post)
        element['posts'] = sorted(element['posts'], key=lambda item: item['post_id'])
        results.append(element)

    text, html = sendmail.create_text("Name", results)

    # with open(r'test.html', 'w') as htmlfile:
    #     htmlfile.write(html)
    sendmail.send("a@b.com", text, html)


def get_time(diff_to_utc=0, day=0):
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


def main():
    database = analyse_game_pages()

    # keys = database[0].keys()
    # with open('db.csv', 'w', newline='') as output_file:
    #     dict_writer = csv.DictWriter(output_file, keys)
    #     dict_writer.writeheader()
    #     dict_writer.writerows(database)

    dbposts.store(database)

    inform_user()


if __name__ == '__main__':
    main()
