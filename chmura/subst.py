from django.core.exceptions import ObjectDoesNotExist
from io import StringIO
from lo3.settings import CACHE_LOCATION, DEBUG
from chmura.models import Alias, SubstitutionType
from .utils import url_request, create_new_session
from datetime import datetime, timedelta
from time import sleep
import chmura.log as log
import pickle
import re
import json
import os
import traceback


##################################################
# Aktualizowanie zastępstw
##################################################
def download_gcall(date, credentials):
    params = {'gpid': credentials['gpid'],
              'gsh': credentials['gsh'],
              'action': 'switch',
              'date': date,
              '_LJSL': '4100'}
    serverResponse = url_request('https://lo3gdynia.edupage.org/gcall',
                                 {'Cookie': 'PHPSESSID=' + credentials['phpsessid']},
                                 params).read().decode('UTF-8')
    return serverResponse


def regeneratePass():
    resp = url_request('https://lo3gdynia.edupage.org/substitution')
    cookie = resp.getheader('Set-Cookie')
    cookie = cookie[cookie.index('PHPSESSID=') + 10: cookie.index(';')]
    resp = resp.read().decode('UTF-8')

    gpid_start = resp.index('gpid=') + 5
    gsh_start = resp.index('gsh=') + 4
    gpid = resp[gpid_start: resp.index('&', gpid_start)]
    gsh = resp[gsh_start: resp.index('"', gsh_start)]

    log.info('New gpid, gsh and cookie', gpid + ' ' + gsh + ' ' + cookie)
    return {'gpid': gpid, 'gsh': gsh, 'phpsessid': cookie}


def updateSubstitution():
    create_new_session()
    credentials = regeneratePass()
    now = datetime.now()
    if not os.path.exists(CACHE_LOCATION + 'substitution'):
        os.makedirs(CACHE_LOCATION + 'substitution')

    # Clear old substitution cache
    for filename in os.listdir(CACHE_LOCATION + 'substitution'):
        name = os.path.splitext(filename)[0]
        if datetime.strptime(name, '%Y-%m-%d').date() < now.date():
            os.remove(CACHE_LOCATION + 'substitution/' + filename)

    # Download substitutions for next 5 days
    for day in range(0, 7):
        period = (now + timedelta(days=day)).strftime('%Y-%m-%d')
        period_unform = now + timedelta(days=day)
        if period_unform.weekday() >= 5:
            with open(CACHE_LOCATION + 'substitution/' + period + '.sbt', 'wb') as f:
                pickle.dump({'dane': [], 'notka': ''}, f, 2)
            continue
        log.info('Pobieranie zastępstw na ' + period)
        jsdb = download_gcall(period, credentials=credentials)
        try:
            result = SubstitutionDB(jsdb).generateSubstitution()
        except ValueError:
            create_new_session()
            credentials = regeneratePass()
            jsdb = download_gcall(period, credentials=credentials)
            try:
                result = SubstitutionDB(jsdb).generateSubstitution()
            except ValueError:
                log.info('Podczas aktualizacji ' + str(day) + '. zastępstwa wystąpił problem', str(traceback.format_exc()))
                with open(CACHE_LOCATION + 'substitution/' + period + '.sbt', 'wb') as f:
                    pickle.dump({'dane': [], 'notka': ''}, f, 2)
                continue
        with open(CACHE_LOCATION + 'substitution/' + period + '.sbt', 'wb') as f:
            pickle.dump(result, f, 2)
        sleep(10)
    log.update_finished('updateSubst', 'ok')


##################################################
# Generowanie dla klienta
##################################################
def verifyInput(date):
    if not re.match(r'^20[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])$', date):
        raise SubstitutionException('Podano datę w niewłaściwym formacie')


def checkIfDateInFuture(date):
    """Checks if given date is not in the past and more than 7 days in future"""
    try:
        date_diff = datetime.strptime(date, '%Y-%m-%d') - datetime.now()
        date_diff = date_diff.days
        if date_diff < -1 or date_diff > 7:
            return False
    except ValueError:
        return False
    return True


def generateDatesDict():
    """Return dictionary containing names and numbers of next 5 working days"""
    data_set = {}
    daysNames = {0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa', 3: 'Czwartek', 4: 'Piątek'}
    for shift in range(0, 7):
        for_date = datetime.now() + timedelta(days=shift)
        if for_date.weekday() >= 5:
            continue
        data_set[daysNames[for_date.weekday()] + ', ' + for_date.strftime('%d.%m.%Y')] = for_date.strftime('%Y-%m-%d')
    return data_set


def loadSubstiution(date):
    verifyInput(date)
    if not os.path.exists(CACHE_LOCATION + 'substitution'):
        os.makedirs(CACHE_LOCATION + 'substitution')
    try:
        with open(CACHE_LOCATION + 'substitution/' + date + '.sbt', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        if DEBUG:
            log.info('Tryb DEBUG aktywny - rozpoczynam pobieranie zastępstw')
            updateSubstitution()
            raise SubstitutionException('Try debugowania jest aktywny. Pobrano zastępstwa. Odśwież stronę.')
        else:
            log.error('Brak pliku z zastępstwami na ' + date)
            raise SubstitutionException('Zastępstwa na żądany dzień nie istnieją')


##################################################
# Aliasy
##################################################
def getAliasOfClass(c):
    return getAlias(c, 'class')


def getAliasOfSubject(x):
    return getAlias(x, 'subject')


def getAlias(c, sel):
    if c == "":
        return c
    x = c.copy()
    try:
        a = Alias.objects.get(orig=c['name'], selector=sel)
        x['name'] = a.alias
        return x
    except ObjectDoesNotExist:
        return x


##################################################
# Klasy
##################################################
class SubstitutionDB:
    def __init__(self, _resp):
        self.serverResponse = _resp

        jsdb_start = self.serverResponse.index('ttdb.fill({') + 10
        jsdb = self.serverResponse[jsdb_start: self.serverResponse.find('"}}});', jsdb_start) + 4]
        jsdb = StringIO(jsdb)
        jsdb = json.load(jsdb)
        self.jsdb = jsdb
        self.jsdb_start = jsdb_start

        self.substitution_types_aliases = {i.orig: i.alias for i in Alias.objects.filter(selector='subst')}
        self.teachers = self.jsdb.get('teachers', {})
        self.classes = self.jsdb.get('classes', {})
        self.subjects = self.jsdb.get('subjects', {})
        self.classrooms = self.jsdb.get('classrooms', {})
        self.periods = self.jsdb.get('periods', {})
        self.subType = self.jsdb.get('substitution_types', {})
        self.breaks = self.jsdb.get('breaks', {})

        for i in ['teachers', 'classes', 'subjects', 'classrooms', 'breaks']:
            exec('self.' + i + '["None"] = ""')

    def getNote(self):
        """Return red note from top of substitutions"""
        try:
            note_start = self.serverResponse.index('.innerHTML="', self.serverResponse.index('.innerHTML="') + 1) + len(
                '.indexHTML="')
            note = self.serverResponse[note_start: self.jsdb_start - 10]
            note = note[0: note.index('";gi')]
            note = self.cleanNote(note)
        except ValueError:
            note = ""
        return note

    @staticmethod
    def cleanNote(note):
        note = note.replace('\\n', '')
        note = note.replace('\\"', '"')
        note = note.replace('<br /> <br />', '<br />')
        return note

    def extractSubstitution(self):
        subst = self.serverResponse[self.serverResponse.find('dt.DataSource(') + 14: self.serverResponse.find(');var dt = new')]
        subst = json.load(StringIO(subst))
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
                    status['typ'] = self.subType.get(zastepstwo[key], {}).copy()
                    if status['typ'].get('short', '') != '' and \
                            not SubstitutionType.objects.filter(name=status['typ'].get('short', '')).exists():
                        SubstitutionType(name=status['typ'].get('short', '')).save()

                    status['typ']['short'] = self.substitution_types_aliases.get(status['typ'].get('short', ''),
                                                                                 status['typ'].get('short', ''))
                elif key == 'period':
                    if type(self.periods) is list:
                        status['lekcja'] = self.periods[int(zastepstwo[key])]
                    elif type(self.periods) is str:
                        status['lekcja'] = zastepstwo[key]
                    else:
                        status['lekcja'] = self.periods.get(zastepstwo[key], 'None')

                elif key == 'subjectid':
                    status['przedmiot'] = [getAliasOfSubject(self.subjects.get(str(zastepstwo[key]), ''))]
                elif key == 'subjectids':
                    status['przedmiot'] = [getAliasOfSubject(self.subjects.get(str(s), '')) for s in zastepstwo[key]]

                elif key == 'teacherid':
                    status['nauczyciel'] = [self.teachers.get(str(zastepstwo[key]), '')]
                elif key == 'teacherids':
                    status['nauczyciel'] = [self.teachers.get(str(s), '') for s in zastepstwo[key]]

                elif key == 'classid':
                    status['klasa'] = [getAliasOfClass(self.classes.get(str(zastepstwo[key]), ''))]
                elif key == 'classids':
                    status['klasa'] = [getAliasOfClass(self.classes.get(str(s), '')) for s in zastepstwo[key]]

                elif key == 'classroomid':
                    status['sala'] = [self.classrooms.get(str(zastepstwo[key]), '')]
                elif key == 'classroomids':
                    status['sala'] = [self.classrooms.get(str(s), '') for s in zastepstwo[key]]

                elif key == 'changes':
                    for z in zastepstwo[key]:
                        if z['column'] == 'teacherid' or z['column'] == 'teacherids':
                            status['old_nauczyciel'].append(self.teachers.get(str(z.get('old', '')), ''))

                            n = self.teachers.get(str(z.get('new', '')))
                            if n not in [None, '']:
                                status['new_nauczyciel'].append(n)
                        elif z['column'] == 'classroomid' or z['column'] == 'classroomids':
                            status['old_sala'].append(self.classrooms.get(str(z.get('old', '')), ''))
                            s = self.classrooms.get(str(z.get('new', '')))
                            if s not in [None, '']:
                                status['new_sala'].append(s)
                        elif z['column'] == 'subjectid' or z['column'] == 'subjectids':
                            status['old_przedmiot'].append(getAliasOfSubject(self.subjects.get(str(z.get('old', '')), '')))

                            p = getAliasOfSubject(self.subjects.get(str(z.get('new', '')), ''))
                            if p not in [None, '']:
                                status['new_przedmiot'].append(p)
                        elif z['column'] == 'classid' or z['column'] == 'classids':
                            status['old_klasa'].append(getAliasOfClass(self.classes.get(str(z.get('old', '')), '')))

                            c = getAliasOfClass(self.classes.get(str(z.get('new', '')), ''))
                            if c is not None:
                                status['new_klasa'].append(c)

            if len(status['klasa']) == 0:
                status['klasa'].append({'name': ''})

            status['przerwa'] = self.breaks.get(zastepstwo.get('break'))
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

        for grupa in zastepstwa:
            if grupa == '':
                zastepstwa[grupa] = sorted(zastepstwa[grupa], key=lambda x: x['przerwa']['name'])
            else:
                zastepstwa[grupa] = sorted(zastepstwa[grupa], key=lambda x: x['lekcja']['name'])

        return dict(sorted(zastepstwa.items()))

    def generateSubstitution(self):
        return {'dane': self.extractSubstitution(), 'notka': self.getNote()}


class SubstitutionException(Exception):
    def __init__(self, message):
        self.message = message
