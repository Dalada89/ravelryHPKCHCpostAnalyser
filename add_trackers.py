from datetime import datetime
from pathlib import PurePath
import json
from database import trackers


def main():
    with open(PurePath('./add_trackers.json'), 'r') as fileobj:
        new_trackers = json.load(fileobj)
    
    for tracker in new_trackers:
        update = False
        filter = {
            'name': tracker['name']
        }
        res = trackers.get(filter=filter)
        if len(res) != 0:
            if res[0]['mail'] == tracker['mail']:
                msg = 'Tracker {name} is already registered. {name} will not be added twice.'
                print(msg.format(name=tracker['name']))
                continue
            else:
                msg = "Tracker {name} is already registered, but the mail address differs. " + \
                    "The stored mail address '{om}' can be replaced by the new one '{nm}'.\n Do you want to do that? [Y/n] -  "
                ans = input(msg.format(name=tracker['name'], om=res[0]['mail'], nm=tracker['mail']))
                if ans.lower() not in ['y', 'yes', 'j', 'ja']:
                    continue
                else:
                    res[0]['mail'] = tracker['mail']
                    tracker = res[0]
                    update = True
        tracker['updated'] = int(datetime.now().timestamp())
        if update:
            trackers.update(tracker)
            msg = 'Tracker {name} updated.'
        else:
            trackers.insert(tracker)
            msg = 'Tracker {name} registered.'
        print(msg.format(name=tracker['name']))


if __name__ == '__main__':
    main()