import urllib.request
import urllib.parse
import json
from io import StringIO
from django.http import Http404
import pickle
import os


def get_cur_path():
    return os.path.dirname(os.path.abspath(__file__))


def save_dict(name, obj):
    with open(get_cur_path() + '/timetables/' + name + '.tt', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict(selector, uid):
    try:
        with open(get_cur_path() + '/timetables/' + selector + uid + '.tt', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        plan = download_and_regenerate_timetable(uid, selector)
        save_dict(selector + uid, plan)
        return plan


def regenerate_pass():
    #TODO: Dodać odnawianie gsh, gpid i ciasteczka
    return


def download_gcall(uid='-22', selector='trieda'):
    params = urllib.parse.urlencode({'gadget':          'MobileTimetableBrowser',
                                     'jscid':           'gi3703455',
                                     'gsh':             'c1b73905',
                                     'action':          'reload',
                                     'num':             '95',
                                     'oblast':          selector,
                                     'id':              uid,
                                     '_LJSL':           '2048'}).encode('UTF-8')
    url = urllib.request.Request('https://lo3gdynia.edupage.org/gcall',
                                 params,
                                 headers={'Cookie': 'PHPSESSID=' + 'deb4ph6ahmglb36aqqfclrrlj5'})
    serverResponse = urllib.request.urlopen(url).read().decode('UTF-8')
    serverResponse = serverResponse[serverResponse.index('{'):serverResponse.find('"verticalPeriods":false}}')+25]
    serverResponse = StringIO(serverResponse)

    timetable = json.load(serverResponse)
    return timetable


def rotateTimeTable(plan):
    plan2 = {}
    for i in range(1,12):
        plan2[str(i)] = {}
        for s in ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']:
            plan2[str(i)][s] = []
    for day in plan:
        for lesson in plan[day]:
            plan2[lesson][day] = plan[day][lesson]
    return plan2


def genTimeTable(uid='-22', selector='trieda'):
    plan = download_gcall(uid, selector)
    teachers = plan['jsdb']['teachers']
    table = plan['data']
    subjects = plan['jsdb']['subjects']
    classrooms = plan['jsdb']['classrooms']
    days = plan['jsdb']['days']
    classes = plan['jsdb']['classes'] if 'classes' in plan['jsdb'] else None

    planJSON = {}

    for day in table:
        dzien = days[int(day['day'])]['name']
        if dzien == 'Sobota' or dzien == 'Niedziela':
            continue
        planJSON[dzien] = {}
        for lessonNumber in range(2, 12):
            planJSON[dzien][str(lessonNumber-1)] = []
            if 'c_' + str(lessonNumber) not in day:
                continue
            lesson = day['c_' + str(lessonNumber)]
            if 'cards' not in lesson:
                continue

            for card in lesson['cards']:
                if card is None:
                    continue
                try:
                    if selector == 'ucitel':
                        planJSON[dzien][str(lessonNumber-1)].append({
                                            'subject': subjects[card['subjects'][0]]['name'],
                                            'classes': [classes[c]['name'] for c in card['classes']],
                                            'classroom': getclassroom(card['classrooms'], classrooms)})
                    else:
                        planJSON[dzien][str(lessonNumber-1)].append({
                                            'subject': subjects[card['subjects'][0]]['name'],
                                            'teacher': teachers[card['teachers'][0]]['firstname'] + ' ' + teachers[card['teachers'][0]]['lastname'],
                                            'classroom': getclassroom(card['classrooms'], classrooms)})
                except KeyError:
                    continue
    return planJSON


def getclassroom(value, classrooms):
    if len(value) == 0:
        return ""
    return classrooms[value[0]]['name']


def download_and_regenerate_timetable(uid, typ):
    try:
        return genTimeTable(uid, typ)
    except ValueError:
        print('[DEBUG]Regenerating gpid, gsh and cookie')
        regenerate_pass()
        try:
            return genTimeTable(uid, typ)
        except ValueError:
            return Http404


def get_timetable(uid, selector):
    return load_dict(selector, uid)


def timetableJob():
    print("[DEBUG]Updating timetable")
    for filename in os.listdir(get_cur_path() + '/timetables'):
        name = os.path.splitext(filename)[0]
        typ = name.replace('*', '-').split('-')
        uid = typ[1]
        typ = typ[0]
        plan = download_and_regenerate_timetable(uid, typ)
        save_dict(filename, plan)
