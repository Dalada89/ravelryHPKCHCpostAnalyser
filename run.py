import json
import pandas as pd
import re
from bs4 import BeautifulSoup
import math
import operator
import os
listOfHouses = ['gryffindor', 'ravenclaw', 'hufflepuff', 'slytherin', 'nqfy']

def analysePage(options):
    """
    This function analyses the page and stores all found projects into a pandas dataframe

    returns a pandas dataframe with all projects of all houses within the defined range.
    
    """
    with open("categories.json", 'r') as file:
        categories = json.load(file)
    with open(options['pagePath'], 'r', encoding='utf-8') as htmlfile:
        content = htmlfile.read()

    df = pd.DataFrame({'id':[],
                    'name': [],
                    'date': [],
                    'project': [],
                    'house': [],
                    'love': []})

    soup = BeautifulSoup(content, 'html.parser')

    posts = soup.find_all(class_="forum_post_row")
    allPostId = []
    for post in posts:
        # Post ID
        tempSoup = BeautifulSoup(str(post), 'html.parser')
        try:
            id = int(tempSoup.find_all(class_="post_number")[0].getText())
            allPostId.append(id)
        except:
            try:
                tempSoup = BeautifulSoup(str(post), 'html.parser')
                body = tempSoup.find_all(class_="empty_post")[0].getText()
                ls = re.findall("delete", body, re.IGNORECASE)
                if len(ls) > 0:
                    errorLog("found deleted post", post)
                    # post deleted
                    # print("found deleted post")
                    continue
            except:
                errorLog("I can't interpretate this post. Something is wrong with it. I pushed in an error.txt file!", post)
                continue
        # Body
        tempSoup = BeautifulSoup(str(post), 'html.parser')
        body = tempSoup.find_all(class_="body forum_post_body")[0].getText()
        # nameBody = re.findall('(?i)name:([a-zA-Z\d\s]+)house:', str(body))[0].replace(' ', '')
        try:
            nameBody = re.findall('(?i)name:?\s?([a-zA-Z\d]{2,40})[,.\s]', str(body))
            nameBody = nameBody[0].replace(' ', '')
            house = re.findall('(?i)house:?\s?([a-zA-Z\d]{2,11})[,.\s]', str(body))
            house = house[0].replace(' ', '')
            house = house.lower()
            if house[-1] == 's':
                house = house[:-1]
            if not house in listOfHouses:
                errorLog("[PostID: " + str(id) + "] Unknown house: " + house + " from " + nameBody, body)

            # verb
            listOfVerbs = {}
            for cat in categories['crafts']:
                ls = re.findall("\s" + cat[0], str(body))
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
                ls = re.findall("\s(" + cat + "[a-z]+)\s", str(body), re.IGNORECASE)
                if len(ls) > 0:
                    project = ls[0].lower()
                    # print(project)
                    break
            # print(body)
        except (IndexError):
            continue
        # Username
        tempSoup = BeautifulSoup(str(post), 'html.parser')
        name = tempSoup.find_all(class_="login")[0].getText()
        if name.lower() != nameBody.lower():
            errorLog('[PostID: ' + str(id) + '] warning: names doesnt match: ' + name + ' <> ' + nameBody, body)
        # PostDate
        tempSoup = BeautifulSoup(str(post), 'html.parser')
        date = tempSoup.find_all(class_="time")
        date = re.findall('<abbr title="([a-zA-Z\d,:\s]+)', str(date))
        love = tempSoup.find_all(class_="reaction_button--love")[0].getText()
        try:
            love = int(re.findall('\(([\d]+)\)', str(love))[0])
        except:
            love = 0
        # print(date)        
        df2 = pd.DataFrame({'id':[id],
                            'name': [name],
                            'date': [date[0]],
                            'project': [project],
                            'house': [house],
                            'love': [love],
                            'verb': [verb]})
        #add new row to end of DataFrame
        df = df.append(df2, ignore_index = True)    
        # print(id + ": " + name)
    
    if options['endPost'] > -1:
        selPost = df[(df.id>=options['startPost'] & df.id<=options['endPost'])]
    else:
        selPost = df[(df.id>=options['startPost'])]
    return selPost

def writePost(df, options, outputFile='message.md'):
    """
    df: pandas dataframe
    options: dictionary
    outputFile: string (optional)

    This function writes all rows of df into a file, defined in outputFile. In the options are some additional parameters.

    returns a string. If an empty string is given in the outputFile, the post message will be returned.
    """
    rank = {}
    for i, h in enumerate(listOfHouses[:-1]):
        rank[h] = len(df[df.house==h])
    rank = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)

    message = "Congratulations for everyone who got their wonderful scores in the past few days!!!\n\n"
    message = message + "Each house worked really hard. The ranking is:\n\n"

    prev = -1
    cnt = 1
    winner = ''
    for i, el in enumerate(rank):
        if el[1] != prev:
            message = message + str(cnt) + ". " + el[0] + " with " + str(el[1]) + " projects\n"
        else:
            message = message + "   " + el[0] + " with " + str(el[1]) + " projects\n"
            cnt -= 1
        if cnt == 1:
            if winner  == '':
                winner = el[0]
            else:
                winner = winner + ', ' + el[0]

        cnt += 1
        prev = el[1]
    message = message + "\nCongratulation to " + winner + "!\n\n"

    message = message + "The most awsomeness projects were made from " + options['sHouse'] + ". Of Course! Lets take a closer look:\n\n"

    postlink = options['url']
    if postlink[-1] != '/':
        postlink = postlink + '/'
    for index, row in df[df.house==options['sHouse'].lower()].iterrows():
        message = message + "[" + row['name'] + "](https://www.ravelry.com/people/" + row['name']+ ") " + row['verb'] + " this super cool "
        sRange = math.floor(float(row['id'])/25)*25+1
        eRange = sRange + 24
        range = str(sRange) + "-" + str(eRange) + "#" + str(row['id']).replace('.0', '')
        message = message + "[" + row['project'] + "](" + postlink + range + "). How cool is that."
        if row['love'] > 4:
            message = message + " Wow!! " + str(row['love']) + " loved this amazing peace of " + row['project'] + ". You have a run, " + row['name'] + ". Keep on crafting.\n\n"
        else:
            message = message + "\n\n"

    message = message + "\nThanks to all of you for your efforts and cant wait to see your amazing crafts on the pitch for next round!!!\n\n"
    message = message + "**" + options['cheers'] + "** - " + options['author']

    if outputFile != '':
        with open(outputFile, 'w') as file:
            file.writelines(message)
        return "File written"
    else:
        return message

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
        
def main():
    """
    main program
    """
    with open('settings.json', 'r') as file:
        opt = json.load(file)
    if os.path.exists("error.txt"):
        os.remove("error.txt")
    df = analysePage(options=opt)
    df.to_csv('submittedProjects.csv')
    writePost(df, opt, outputFile='message.md')

    print("File message.md written.")

    return None
    
if __name__ == '__main__':
    main()