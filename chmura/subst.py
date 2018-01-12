# TODO: Dodać zastępstwa na przerwach

import urllib.request
import urllib.parse
from io import StringIO
from django.http import Http404
from chmura.models import Settings
import pickle
import os
import re
import json
from datetime import datetime, timedelta


def get_cur_path():
    return os.path.dirname(os.path.abspath(__file__))


def save_dict(name, obj):
    with open(get_cur_path() + '/substitution/' + name + '.sbt', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict(date):
    try:
        with open(get_cur_path() + '/substitution/' + date + '.sbt', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        zast = download_and_regenerate_subst(date)
        save_dict(date, zast)
        return zast


def get_substitution(date):
    if re.match(r'^20[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])$', date) is None:
        raise Http404
    return load_dict(date)


def download_and_regenerate_subst(date):
    try:
        return download_subst(date)
    except ValueError:
        print('[DEBUG]Regenerating gpid, gsh and cookie')
        regenerate_pass()
        try:
            return download_subst(date)
        except ValueError:
            return {'dane': [{'przedmiot': [{'name': 'W tym dniu nie'}], 'nauczyciel': [{'name': 'ma żadnych zastępstw.'}]}], 'notka': ''}


def regenerate_pass():
    url = urllib.request.Request('https://lo3gdynia.edupage.org/substitution')
    resp = urllib.request.urlopen(url)
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
    print(gpid, gsh, cookie)


def download_subst(date, debug=False):
    settings = Settings.objects.all()[0]
    params = urllib.parse.urlencode({'gpid': settings.gpid,
                                     'gsh': settings.gsh,
                                     'action': 'switch',
                                     'date': date,
                                     '_LJSL': '2052'}).encode('UTF-8')
    url = urllib.request.Request('https://lo3gdynia.edupage.org/gcall',
                                 params,
                                 headers={'Cookie': 'PHPSESSID=' + settings.phpsessid})
    serverResponse = urllib.request.urlopen(url).read().decode('UTF-8')
    if debug:
        print(serverResponse)

    jsdb_start = serverResponse.index('ttdb.fill({') + 10
    jsdb = serverResponse[jsdb_start: serverResponse.find('"}}});', jsdb_start) + 4]
    jsdb = StringIO(jsdb)
    jsdb = json.load(jsdb)

    teachers = jsdb['teachers']
    classes = jsdb['classes']
    subjects = jsdb['subjects']
    classrooms = jsdb['classrooms']
    periods = jsdb['periods']
    subType = jsdb['substitution_types']
    if debug:
        print(periods)

    # Pobieranie czerwonej notatki
    note_start = serverResponse.index('.innerHTML="', serverResponse.index('.innerHTML="') + 1) + len('.indexHTML="')
    note = serverResponse[note_start: jsdb_start - 10]
    note = note[0: note.index('";gi')]
    note = note.replace('\\n', '')

    subst = serverResponse[serverResponse.find('dt.DataSource(') + 14:serverResponse.find(');var dt = new')]
    subst = StringIO(subst)
    subst = json.load(subst)

    zastepstwa = []

    for zastepstwo in subst:
        status = {'new_przedmiot': [],
                  'new_nauczyciel': [],
                  'old_nauczyciel': [],
                  'old_przedmiot': [],
                  'new_sala': [],
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
                status['typ'] = subType.get(zastepstwo[key], "")
            elif key == 'period':
                if type(periods) is list:
                    status['lekcja'] = periods[int(zastepstwo[key])]
                else:
                    status['lekcja'] = periods[zastepstwo[key]]

            elif key == 'subjectid':
                status['przedmiot'] = [subjects[zastepstwo[key]]]
            elif key == 'subjectids':
                status['przedmiot'] = [subjects[str(s)] for s in zastepstwo[key]]

            elif key == 'teacherid':
                status['nauczyciel'] = [teachers[zastepstwo[key]]]
            elif key == 'teacherids':
                status['nauczyciel'] = [teachers[str(s)] for s in zastepstwo[key]]

            elif key == 'classid':
                status['klasa'] = [classes[zastepstwo[key]]]
            elif key == 'classids':
                status['klasa'] = [classes[str(s)] for s in zastepstwo[key]]

            elif key == 'classroomid':
                status['sala'] = [classrooms[zastepstwo[key]]]
            elif key == 'classroomids':
                status['sala'] = [classrooms[str(s)] for s in zastepstwo[key]]

            elif key == 'changes':
                for z in zastepstwo[key]:
                    if z['column'] == 'teacherid' or z['column'] == 'teacherids':
                        status['old_nauczyciel'].append(teachers[str(z['old'])])

                        n = teachers.get(str(z.get('new')))
                        if n is not None:
                            status['new_nauczyciel'].append(n)
                    elif z['column'] == 'classroomid' or z['column'] == 'classroomids':
                        status['new_sala'].append({'old': classrooms[str(z['old'])],
                                                   'new': classrooms.get(str(z.get('new', None)))})
                    elif z['column'] == 'subjectid' or z['column'] == 'subjectids':
                        status['old_przedmiot'].append(subjects[str(z['old'])])

                        p = subjects.get(str(z.get('new')))
                        if p is not None:
                            status['new_przedmiot'].append(p)

        if debug:
            print('Klasa:', status.get('klasa', None), '\t', 'Lekcja:', status.get('lekcja', None), '\n',
                  'Nauczyciel:', status['nauczyciel'], '->', status['new_nauczyciel'], '\n',
                  'Przedmiot:', status.get('przedmiot', None), '->', status['new_przedmiot'], '\n',
                  'Sala:', status['sala'], '->', status['new_sala'], '\n',
                  'Typ zastępstwa:', status['typ'], '\t', 'Notka: ', status.get('notka', None), '\n\n')
        if len(status['klasa']) == 0:
            status['klasa'].append({'name': ''})

        zastepstwa.append(status)
    posortowane = sorted(zastepstwa, key=lambda k: k['klasa'][0]['name'])
    return {'dane': posortowane, 'notka': note}


def updateJob():
    now = datetime.now()
    for filename in os.listdir(get_cur_path() + '/substitution'):
        name = os.path.splitext(filename)[0]
        if datetime.strptime(name, '%Y-%m-%d').date() < now.date():
            print('[DEBUG]Deleting old substitution cache')
            os.remove(get_cur_path() + '/substitution/' + filename)

    continueDownloading = True
    for i in range(0, 7):
        period = now + timedelta(days=i)
        print('[DEBUG]Downloading new substitution for', period.strftime('%Y-%m-%d'))
        if continueDownloading:
            zast = download_and_regenerate_subst(period.strftime('%Y-%m-%d'))
            if zast == [{'przedmiot': [{'name': 'W tym dniu nie'}], 'nauczyciel': [{'name': 'ma żadnych zastępstw.'}]}]:
                continueDownloading = False
        else:
            zast = [{'przedmiot': [{'name': 'W tym dniu nie'}], 'nauczyciel': [{'name': 'ma żadnych zastępstw.'}]}]
        save_dict(period.strftime('%Y-%m-%d'), zast)
