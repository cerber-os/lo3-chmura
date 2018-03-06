import json
from io import StringIO
from django.http import Http404
import pickle
from random import randint
from .utils import *
from time import sleep
import chmura.log as log
from chmura.colors import get_color
from chmura.updateids import load_ids
# import shutil
from django.core.exceptions import ObjectDoesNotExist
from chmura.models import Alias, Settings


def save_dict(name, obj):
    if not os.path.exists(get_cur_path() + '/../cache/timetables'):
        os.makedirs(get_cur_path() + '/../cache/timetables')
    name = name.replace('*', '#')
    with open(get_cur_path() + '/../cache/timetables/' + name + '.tt', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict(selector, uid):
    if not os.path.exists(get_cur_path() + '/../cache/timetables'):
        os.makedirs(get_cur_path() + '/../cache/timetables')
    try:
        with open(get_cur_path() + '/../cache/timetables/' + selector + uid.replace('*', '#') + '.tt', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        if DEBUG or selector == 'student':
            log.info("Downloading timetable " + selector + ':' + uid + ' on demand')
            if getReversedStudent(load_ids('students'), uid) == "null":
                raise Http404
            plan = download_and_regenerate_timetable(uid, selector)
            save_dict(selector + uid, plan)
        else:
            raise Http404
        return plan


def regenerate_pass():
    credentials = {}

    # JSCID
    jscid = [randint(0, 9) for _ in range(0, 7)]
    credentials['jscid'] = 'gi' + ''.join([str(t) for t in jscid])

    # Cookie
    resp = url_request('https://lo3gdynia.edupage.org/mobile')
    cookie = resp.getheader('Set-Cookie')
    credentials['cookie'] = cookie[cookie.index('PHPSESSID=') + 10: cookie.index(';')]
    resp = resp.read().decode('UTF-8')

    # Gsh
    gsh_start = resp.index('gsh=')
    credentials['gsh'] = resp[gsh_start + 4: resp.index('"', gsh_start)]

    return credentials


def retrieve_pass():
    for _ in range(0, 3):
        try:
            credentials = regenerate_pass()
            return credentials
        except json.JSONDecodeError:
            log.info('Retrieving password failed. Trying again...')
    else:
        log.error('Failed to retrieve password!!!')
        return None


def get_timetable_newest_version():
    serverResponse = url_request('https://lo3gdynia.edupage.org/timetable/').read().decode('UTF-8')
    versions = serverResponse[serverResponse.index('"text":"następny tydzień",') + len('"text":"następny tydzień",'):
                              serverResponse.index('[\n{"text":"Stara wersja",') + len('[\n{"text":"Stara wersja",')]
    versions = versions[versions.index('}],') + len('}],'):]
    versionStart = versions.index('"obj":') + len('"obj":')
    version = versions[versionStart: versions.index('}', versionStart)]
    log.info('Nowa wersja planu to: ' + str(version))
    Settings.objects.filter().update(timetableVersion=version)


def download_gcall(uid='-22', selector='trieda', credentials=None):
    if credentials is None:
        credentials = regenerate_pass()
    if len(Settings.objects.all()) == 0:
        unikalnanazwazmiennej = Settings()
        unikalnanazwazmiennej.save()
    settings = Settings.objects.all()[0]
    params = {'gadget': 'MobileTimetableBrowser',
              'jscid': credentials['jscid'],
              'gsh': credentials['gsh'],
              'action': 'reload',
              'oblast': selector,
              'id': uid,
              '_LJSL': '2048',
              'num': settings.timetableVersion}
    serverResponse = url_request('https://lo3gdynia.edupage.org/gcall',
                                 {'Cookie': 'PHPSESSID=' + credentials['cookie']},
                                 params).read().decode('UTF-8')
    serverResponse = serverResponse[serverResponse.index('{'):serverResponse.find('"verticalPeriods":false}}')+25]
    serverResponse = StringIO(serverResponse)

    timetable = json.load(serverResponse)
    return timetable


def rotateTimeTable(plan):
    plan2 = {}
    for i in range(1, 12):
        plan2[str(i)] = {}
        for s in ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']:
            plan2[str(i)][s] = []
    for day in plan:
        for lesson in plan[day]:
            plan2[lesson][day] = plan[day][lesson]
    return plan2


def genTimeTable(uid='-22', selector='trieda', credentials=None):
    plan = download_gcall(uid, selector, credentials)
    table = plan['data']
    teachers = plan['jsdb'].get('teachers', {})
    subjects = plan['jsdb'].get('subjects', {})
    classrooms = plan['jsdb'].get('classrooms', {})
    days = plan['jsdb'].get('days', {})
    classes = plan['jsdb'].get('classes', {})

    planJSON = {}

    for day in table:
        dzien = days[int(day['day'])]['name']
        if dzien == 'Sobota' or dzien == 'Niedziela':
            continue
        planJSON[dzien] = {}
        for lessonNumber in range(1, 16):
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
                                            'subject': getSubject(subjects[card['subjects'][0]]['name']),
                                            'color': get_color(subjects[card['subjects'][0]]['name'],
                                                               subjects[card['subjects'][0]]['color']),
                                            'classes': [getClass(classes[c]['name']) for c in card['classes']],
                                            'classroom': getclassroom(card['classrooms'], classrooms)})
                    else:
                        planJSON[dzien][str(lessonNumber-1)].append({
                                            'subject': getSubject(subjects[card['subjects'][0]]['name']),
                                            'color': get_color(subjects[card['subjects'][0]]['name'],
                                                               subjects[card['subjects'][0]]['color']),
                                            'teacher': getteachername(card, teachers),
                                            'classroom': getclassroom(card['classrooms'], classrooms)})
                except KeyError:
                    continue

    planJSON = clean_timetable(planJSON)
    return planJSON


def getClass(c):
    return getAlias(c, 'class')


def getSubject(x):
    return getAlias(x, 'subject')


def getAlias(c, sel):
    if c == "":
        return c
    try:
        a = Alias.objects.get(orig=c, selector=sel)
        return a.alias
    except ObjectDoesNotExist:
        return c


def getclassroom(value, classrooms):
    if len(value) == 0:
        return ""
    return classrooms.get(value[0], {}).get('name')


def getteachername(card, teachers):
    ret = ""
    for t in card['teachers']:
        ret += (teachers.get(t, {}).get('firstname')[0:1] or '') + '. ' + teachers.get(t, {}).get('lastname') + ', '
    ret = ret[:-2]
    return ret


def clean_column(plan, number):
    emptyCol = True
    effect = False
    for day in plan:
        if plan[day][str(number)]:
            emptyCol = False
    if emptyCol:
        for day in plan:
            del(plan[day][str(number)])
        effect = True
    return plan, effect


def clean_timetable(plan):
    for i in range(14, 1, -1):
        (plan, cont) = clean_column(plan, i)
        if not cont:
            break
    (plan, cont) = clean_column(plan, 0)
    return plan


def download_and_regenerate_timetable(uid, typ, credentials=None):
    try:
        return genTimeTable(uid, typ, credentials)
    except ValueError:
        log.warning('Unable to download timetable: ' + uid + ' - timetable:dart')
        raise Http404


def get_timetable(uid, selector):
    return load_dict(selector, uid)


def timetableJob():
    create_new_session()
    get_timetable_newest_version()
    log.info("Updating timetable")
    credentials = retrieve_pass()
    if credentials is None:
        return

    connection_count = 0

    if not DEBUG:
        # if os.path.exists(get_cur_path() + '/../cache'):
        #    shutil.rmtree(get_cur_path() + '/../cache/timetables')

        targets = {'classes':  'trieda',
                   'teachers': 'ucitel'}

        for typ in targets.keys():
            ids = load_ids(typ)
            for pk in list(ids.values()):
                try:
                    log.info('Downloading timetable: ' + pk)
                    plan = download_and_regenerate_timetable(pk, targets[typ], credentials)
                    save_dict(targets[typ] + pk.replace('#', '-'), plan)
                    connection_count += 1
                    if connection_count % 5 == 0:
                        create_new_session()
                        credentials = retrieve_pass()
                        if credentials is None:
                            return
                    sleep(3)
                except Exception as e:
                    print(e)
                    continue

    if DEBUG:
        for filename in os.listdir(get_cur_path() + '/../cache/timetables'):
            name = os.path.splitext(filename)[0]
            typ = name.replace('#', '-').split('-')
            uid = typ[1]
            typ = typ[0]

            if '#' in name:
                uid = '*' + str(uid)
            elif '-' in name:
                uid = '-' + str(uid)
            else:
                log.error('Could not determine uid. Omitting update for: ' + name)
                continue

            log.info('Downloading timetable: ' + name)
            plan = download_and_regenerate_timetable(uid, typ, credentials)
            save_dict(name, plan)
            connection_count += 1
            if connection_count % 10 == 0:
                create_new_session()
                credentials = retrieve_pass()
                if credentials is None:
                    return
            sleep(2)
