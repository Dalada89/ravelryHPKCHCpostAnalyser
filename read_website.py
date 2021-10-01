import json
# import pandas as pd
import re
from bs4 import BeautifulSoup
import datetime
import custom_error as ce
# import math
# from dateutil import parser, tz
# from datetime import datetime
# import pytz
# import operator
# import os
with open('listOfHouses.json', 'r') as file:
    listOfHouses = json.load(file)


def analysePage(content, further_data):
    """
    This function analyses the page and stores all found projects into a pandas dataframe

    returns a pandas dataframe with all projects of all houses within the defined range.

    """
    with open("categories.json", 'r') as file:
        categories = json.load(file)

    # df = pd.DataFrame({
    #     'id': [],
    #     'name': [],
    #     'date': [],
    #     'project': [],
    #     'house': [],
    #     'love': []})

    soup = BeautifulSoup(content, 'html.parser')

    posts = soup.find_all(class_="forum_post_row")
    allPostId = []
    lst = []
    for post in posts:
        # Post ID
        tempSoup = BeautifulSoup(str(post), 'html.parser')
        try:
            id = int(tempSoup.find_all(class_="post_number")[0].getText())
            allPostId.append(id)
        except IndexError:
            try:
                tempSoup = BeautifulSoup(str(post), 'html.parser')
                body = tempSoup.find_all(class_="empty_post")[0].getText()
                ls = re.findall("delete", body, re.IGNORECASE)
                if len(ls) > 0:
                    errorLog("found deleted post", post)
                    # post deleted
                    # print("found deleted post")
                    continue
            except IndexError:
                errorLog("I can't interpretate this post. Something is wrong with it. I pushed in an error.txt file!", post)
                continue
        # Body
        tempSoup = BeautifulSoup(str(post), 'html.parser')
        body = tempSoup.find_all(class_="body forum_post_body")[0].getText()
        name = tempSoup.find_all(class_="login")[0].getText()
        # nameBody = re.findall('(?i)name:([a-zA-Z\d\s]+)house:', str(body))[0].replace(' ', '')
        try:
            # nameBody = re.findall(r'(?i)name:?\s?([a-zA-Z\d]{2,40})[,.\s]', str(body))
            # nameBody = nameBody[0].replace(' ', '')
            housePattern = r":?(?:name)?[\s:-]*?" + name + r"[,.\s\n]*(?:house)?\s?[\s:-]*?([a-zA-Z\d]{2,11})[,.\s]"
            # print(housePattern)
            house = re.findall(housePattern, str(body), re.IGNORECASE)

            house = house[0].replace(' ', '')
            house = house.lower()
            if house[-1] == 's' and len(house) > 3:
                house = house[:-1]
            if house not in listOfHouses:
                errorLog("[PostID: " + str(id) + "] Unknown house: " + house + " from " + name, body)
                continue

            # verb
            listOfVerbs = {}
            for cat in categories['crafts']:
                ls = re.findall(r"\s" + cat[0], str(body))
                if len(ls) > 0:
                    listOfVerbs[cat[2]] = len(ls)
            listOfVerbs = sorted(listOfVerbs.items(), key=lambda ele: ele[1])
            # print(listOfVerbs)
            verb = ''
            if len(listOfVerbs) > 0:
                verb = listOfVerbs[0][0]
                # print(verb)
            else:
                verb = 'made'

            # project
            project = 'thing'
            for cat in categories['projects']:
                ls = re.findall(r'\s(' + cat + r'[a-z]+)\s', str(body), re.IGNORECASE)
                if len(ls) > 0:
                    project = ls[0].lower()
                    # print(project)
                    break
            # print(body)
        except (IndexError):
            continue
        # Username
        # tempSoup = BeautifulSoup(str(post), 'html.parser')
        # name = tempSoup.find_all(class_="login")[0].getText()
        # if name.lower() != nameBody.lower():
        #     errorLog('[PostID: ' + str(id) + '] warning: names doesnt match: ' + name + ' <> ' + nameBody, body)
        # PostDate
        tempSoup = BeautifulSoup(str(post), 'html.parser')
        date_str = tempSoup.find_all(class_="time")
        date_str = re.findall(r'<abbr title="([a-zA-Z\d,:\s]+)', str(date_str))[0]
        try:
            date_unix = interpretate_date(date_str)
        except ce.DateError as exc:
            date_unix = -1
            print(exc)
        love = tempSoup.find_all(class_="reaction_button--love")[0].getText()
        try:
            love = int(re.findall(r'\(([\d]+)\)', str(love))[0])
        except IndexError:
            love = 0
        # print(date)
        dct = {
            'class_id': int(further_data['class_id']),
            'post_id': int(id),
            'name': name,
            'date': date_unix,
            'project': project,
            'house': house,
            'loved': love,
            'verb': verb,
            'url': further_data['url'] + '#' + str(id)}
        # a dd new row to end of DataFrame
        lst.append(dct)
        # print(id + ": " + name)
    # df = pd.DataFrame(lst)
    # print(df)
    # if options['endPost'] > -1:
    #     selPost = df[(df.id >= options['startPost'] & df.id <= options['endPost'])]
    # else:
    #     selPost = df[(df.id >= options['startPost'])]
    return lst


def errorLog(msg, log):
    """
    msg: str, Information about the error
    log: not defined, normaly the body or the complete post.

    This function write all errors in a file. the file will be appended by each error.
    Also the msg is printed into the console.

    return None
    """
    logEntry = msg + ':\n' + str(log) + '\n ________________________________________________________________________________________________\n'
    with open('error.txt', 'a') as f:
        f.write(logEntry)
    print(msg)

    return None


def interpretate_date(date_ravelry):
    """
    """
    pattern = r",\s(\w+)\s+(\d{1,2})\s+(\d{4})?[\sat]+(\d{1,2}:\d{2}\s[APap][mM]$)"
    # pattern = r",\s(\w+)"#\s+(\d{1,2})\s+(\d{4})?[\sat]+(\d{1,2}:\d{2}\s[APap][mM]$)"
    date_comp = re.search(pattern, date_ravelry)
    date_dict = {
        'year': str(date_comp[3]),
        'month': str(date_comp[1]),
        'day': str(date_comp[2]),
        'time': str(date_comp[4])
    }
    if date_comp[3] is None:
        date_dict['year'] = str(datetime.date.today().year)
    date_str = date_dict['day'] + ". " + date_dict['month'] + " " + date_dict['year'] + ", " + date_dict['time']
    # print("The Date is: " + date_str)

    date_date = datetime.datetime.strptime(date_str, '%d. %B %Y, %I:%M %p')
    date_unix = int(date_date.timestamp())

    if date_unix > int(datetime.datetime.now().timestamp()):
        raise ce.DateError('Date is in the future.')
    else:
        return date_unix


def main():
    # ravelry_year = 'Tuesday, September  1 2020 at  1:55 AM'
    ravelry = 'Sunday, September  5 at  7:12 AM'
    timestamp = 1630818720
    try:
        val = interpretate_date(ravelry)
    except ce.DateError as exc:
        val = -1
        print(exc)

    if val == timestamp:
        print("is equal")
    else:
        print("is not equal")
    print(str(val) + " == " + str(timestamp))


if __name__ == '__main__':
    main()
