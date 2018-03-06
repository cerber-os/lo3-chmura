from io import StringIO
from django.http import Http404
from chmura.models import Alias
import pickle
import re
import json
from datetime import datetime, timedelta
from .utils import *
from time import sleep
import chmura.log as log
from django.core.exceptions import ObjectDoesNotExist


def save_dict(name, obj):
    if not os.path.exists(get_cur_path() + '/../cache/substitution'):
        os.makedirs(get_cur_path() + '/../cache/substitution')
    with open(get_cur_path() + '/../cache/substitution/' + name + '.sbt', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict(date):
    if not os.path.exists(get_cur_path() + '/../cache/substitution'):
        os.makedirs(get_cur_path() + '/../cache/substitution')
    try:
        with open(get_cur_path() + '/../cache/substitution/' + date + '.sbt', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        zast = download_and_regenerate_subst(date)
        save_dict(date, zast)
        return zast


def get_substitution(date):
    if re.match(r'^20[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])$', date) is None:
        log.info('Incorrect date was given - subst:30')
        raise Http404
    return load_dict(date)


def download_and_regenerate_subst(date):
    try:
        return download_subst(date)
    except ValueError:
        log.info('Regenerating gpid, gsh and cookie')
        regenerate_pass()
        try:
            return download_subst(date)
        except ValueError:
            return {'dane': [], 'notka': ''}


def regenerate_pass():
    resp = url_request('https://lo3gdynia.edupage.org/substitution')
    cookie = resp.getheader('Set-Cookie')
    cookie = cookie[cookie.index('PHPSESSID=') + 10: cookie.index(';')]
    resp = resp.read().decode('UTF-8')

    gpid_start = resp.index('gpid=') + 5
    gsh_start = resp.index('gsh=') + 4
    gpid = resp[gpid_start: resp.index('&', gpid_start)]
    gsh = resp[gsh_start: resp.index('"', gsh_start)]

    Settings.objects.filter().update(gpid=gpid,
                                     gsh=gsh,
                                     phpsessid=cookie)
    log.info('New gpid, gsh and cookie', gpid + ' ' + gsh + ' ' + cookie)


def download_subst(date):
    if len(Settings.objects.all()) == 0:
        unikalnanazwazmiennej = Settings()
        unikalnanazwazmiennej.save()
    settings = Settings.objects.all()[0]
    substitution_types_aliases = {i.orig: i.alias for i in Alias.objects.filter(selector='subst')}
    params = {'gpid': settings.gpid,
              'gsh': settings.gsh,
              'action': 'switch',
              'date': date,
              '_LJSL': '2052'}
    serverResponse = url_request('https://lo3gdynia.edupage.org/gcall',
                                 {'Cookie': 'PHPSESSID=' + settings.phpsessid},
                                 params).read().decode('UTF-8')
    log.debug(serverResponse)

    jsdb_start = serverResponse.index('ttdb.fill({') + 10
    jsdb = serverResponse[jsdb_start: serverResponse.find('"}}});', jsdb_start) + 4]
    jsdb = StringIO(jsdb)
    jsdb = json.load(jsdb)

    teachers = jsdb.get('teachers', {})
    classes = jsdb.get('classes', {})
    subjects = jsdb.get('subjects', {})
    classrooms = jsdb.get('classrooms', {})
    periods = jsdb.get('periods', {})
    subType = jsdb.get('substitution_types', {})
    breaks = jsdb.get('breaks', {})

    for i in ['teachers', 'classes', 'subjects', 'classrooms', 'breaks']:
        exec(i + '["None"] = ""')

    # Pobieranie czerwonej notatki
    try:
        note_start = serverResponse.index('.innerHTML="', serverResponse.index('.innerHTML="') + 1) + len(
            '.indexHTML="')
        note = serverResponse[note_start: jsdb_start - 10]
        note = note[0: note.index('";gi')]
        note = note.replace('\\n', '')
        note = note.replace('\\"', '"')
        note = note.replace('<br /> <br />', '<br />')
    except ValueError:
        note = ""

    subst = serverResponse[serverResponse.find('dt.DataSource(') + 14:serverResponse.find(');var dt = new')]
    subst = StringIO(subst)
    subst = json.load(subst)

    # zastepstwa = []
    zastepstwa = {}

    for zastepstwo in subst:
        status = {'new_przedmiot': [],
                  'new_nauczyciel': [],
                  'old_nauczyciel': [],
                  'old_przedmiot': [],
                  'new_sala': [],
                  'old_sala': [],
                  'old_klasa': [],
                  'new_klasa': [],
                  'przedmiot': [],
                  'lekcja': [],
                  'notka': '',
                  'klasa': [], }
        for key in zastepstwo:
            if key == 'cancelled':
                status['anulowano'] = zastepstwo[key]
            elif key == 'note':
                status['notka'] = zastepstwo[key]
            elif key == 'substitution_typeid':
                status['typ'] = subType.get(zastepstwo[key], {})
                status['typ']['short'] = substitution_types_aliases.get(status['typ'].get('short', ''),
                                                                        status['typ'].get('short', ''))
            elif key == 'period':
                if type(periods) is list:
                    status['lekcja'] = periods[int(zastepstwo[key])]
                elif type(periods) is str:
                    status['lekcja'] = zastepstwo[key]
                else:
                    status['lekcja'] = periods.get(zastepstwo[key], 'None')

            elif key == 'subjectid':
                status['przedmiot'] = [getSubject(subjects.get(str(zastepstwo[key]), ''))]
            elif key == 'subjectids':
                status['przedmiot'] = [getSubject(subjects.get(str(s), '')) for s in zastepstwo[key]]

            elif key == 'teacherid':
                status['nauczyciel'] = [teachers.get(str(zastepstwo[key]), '')]
            elif key == 'teacherids':
                status['nauczyciel'] = [teachers.get(str(s), '') for s in zastepstwo[key]]

            elif key == 'classid':
                status['klasa'] = [getClass(classes.get(str(zastepstwo[key]), ''))]
            elif key == 'classids':
                status['klasa'] = [getClass(classes.get(str(s), '')) for s in zastepstwo[key]]

            elif key == 'classroomid':
                status['sala'] = [classrooms.get(str(zastepstwo[key]), '')]
            elif key == 'classroomids':
                status['sala'] = [classrooms.get(str(s), '') for s in zastepstwo[key]]

            elif key == 'changes':
                for z in zastepstwo[key]:
                    if z['column'] == 'teacherid' or z['column'] == 'teacherids':
                        status['old_nauczyciel'].append(teachers.get(str(z.get('old', '')), ''))

                        n = teachers.get(str(z.get('new', '')))
                        if n not in [None, '']:
                            status['new_nauczyciel'].append(n)
                    elif z['column'] == 'classroomid' or z['column'] == 'classroomids':
                        status['old_sala'].append(classrooms.get(str(z.get('old', '')), ''))
                        s = classrooms.get(str(z.get('new', '')))
                        if s not in [None, '']:
                            status['new_sala'].append(s)
                    elif z['column'] == 'subjectid' or z['column'] == 'subjectids':
                        status['old_przedmiot'].append(getSubject(subjects.get(str(z.get('old', '')), '')))

                        p = getSubject(subjects.get(str(z.get('new', '')), ''))
                        if p not in [None, '']:
                            status['new_przedmiot'].append(p)
                    elif z['column'] == 'classid' or z['column'] == 'classids':
                        status['old_klasa'].append(getClass(classes.get(str(z.get('old', '')), '')))

                        c = getClass(classes.get(str(z.get('new', '')), ''))
                        if c is not None:
                            status['new_klasa'].append(c)

        log.debug('Klasa: ' + str(status.get('klasa', 'None')) + '\t' + 'Lekcja: ' + str(
            status.get('lekcja', 'None')) + '\n' +
                  'Nauczyciel: ' + str(status['nauczyciel']) + ' -> ' + str(status['new_nauczyciel']) + '\n' +
                  'Przedmiot :' + str(status.get('przedmiot', 'None')) + ' -> ' + str(status['new_przedmiot']) + '\n' +
                  'Sala :' + str(status['sala']) + ' -> ' + str(status['new_sala']) + '\n' +
                  'Typ zastępstwa: ' + str(status.get('typ', 'None')) + '\n\n')

        if len(status['klasa']) == 0:
            status['klasa'].append({'name': ''})

        status['przerwa'] = breaks.get(zastepstwo.get('break'))
        status['klasa'] = sorted(status['klasa'], key=lambda s: s['name'])

        k = ""
        for s in status['klasa']:
            for l in status['old_klasa']:
                if s['name'] == l['name']:
                    k += '<s>' + s['name'] + '</s>, '
                    break
            else:
                k += s['name'] + ', '
        k = k[0:-2]
        status['displayname'] = k

        k = ""
        for s in status['klasa']:
            k += s['name'] + ', '
        k = k[0:-2]
        try:
            zastepstwa[k].append(status)
        except KeyError:
            zastepstwa[k] = [status]
    posortowane = dict(sorted(zastepstwa.items()))
    return {'dane': posortowane, 'notka': note}


def getClass(c):
    return getAlias(c, 'class')


def getSubject(x):
    return getAlias(x, 'subject')


def getAlias(c, sel):
    if c == "":
        return c
    try:
        a = Alias.objects.get(orig=c['name'], selector=sel)
        c['name'] = a.alias
        return c
    except ObjectDoesNotExist:
        return c


def updateJob():
    create_new_session()
    now = datetime.now()
    if not os.path.exists(get_cur_path() + '/../cache/substitution'):
        os.makedirs(get_cur_path() + '/../cache/substitution')
    for filename in os.listdir(get_cur_path() + '/../cache/substitution'):
        name = os.path.splitext(filename)[0]
        if datetime.strptime(name, '%Y-%m-%d').date() < now.date():
            log.info('Deleting old substitution cache')
            os.remove(get_cur_path() + '/../cache/substitution/' + filename)

    continueDownloading = True
    for i in range(0, 7):
        period = now + timedelta(days=i)
        if period.weekday() >= 5: 
            period += timedelta(days=7 - period.weekday())
        if continueDownloading:
            log.info('Downloading new substitution for', period.strftime('%Y-%m-%d'))
            zast = download_and_regenerate_subst(period.strftime('%Y-%m-%d'))
            if zast == {'dane': [], 'notka': ''}:
                continueDownloading = False
        else:
            log.info('Omitting update for', period.strftime('%Y-%m-%d'))
            zast = {'dane': [], 'notka': ''}
        save_dict(period.strftime('%Y-%m-%d'), zast)
        sleep(2)
