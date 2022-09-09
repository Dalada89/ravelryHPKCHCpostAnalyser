from pathlib import PurePath
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime
import pandas as pd
import json
import common_functions as cf


with open('listOfHouses.json', 'r') as fileobj:
    listOfHouses = json.load(fileobj)
with open('./report/style.json', 'r') as fileobj:
    style = json.load(fileobj)


def plot_timeline(data, course, savedir):
    """
    This function shall create a diagram with a timeline of all four houses
    """

    data = sorted(data, key=lambda item: item['date'])
    month = datetime.fromtimestamp(data[0]['date']).month
    year = datetime.fromtimestamp(data[0]['date']).year
    last_day = cf.get_last_date_of_month(year, month)

    counter = {}
    for house in listOfHouses:
        counter[house] = 0

    prepared = []
    cur_day = 1
    for item in data:
        day = datetime.fromtimestamp(item['date']).day
        if day > cur_day:
            el = {}
            el['day'] = cur_day
            for house in listOfHouses:
                el[house] = counter[house]
            prepared.append(el)
            cur_day = day
        counter[item['house']] += 1

    df = pd.DataFrame(prepared)

    fig, ax = plt.subplots()
    for house in listOfHouses:
        if house in ['sos', 'nqfy']:
            continue
        ax.plot(df['day'], df[house], linestyle='solid', color=style['houses'][house], label=house)
    ax.grid()
    ax.legend()
    ax.set_ylabel('Submissons')
    ax.set_xlabel('Day')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(1, last_day.day)
    ax.set_xticks([1, 7, 14, 21, 28, last_day.day])
    ax.set_title(course['title'])
    savedir = PurePath(savedir)
    plt.savefig(savedir.joinpath('timeline.png'), dpi=300)
