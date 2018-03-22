import json
import re
from io import StringIO
import os
import pickle
from lo3.settings import CACHE_LOCATION, DEBUG
import chmura.log as log
from chmura.colors import get_color
from chmura.models import Alias
from django.core.exceptions import ObjectDoesNotExist
from chmura.utils import url_request
from chmura.updateids import load_ids


##################################################
# Aktualizowanie planu lekcji
##################################################
def download_gcall():
    ##################################################
    # Pozyskanie numeru najnowszego planu
    ##################################################
    serverResponseOrig = url_request('https://lo3gdynia.edupage.org/timetable/')
    serverResponse = serverResponseOrig.read().decode('UTF-8')
    versions = serverResponse[serverResponse.index('"text":"następny tydzień",') + len('"text":"następny tydzień",'):
                              serverResponse.index('[\n{"text":"Stara wersja",') + len('[\n{"text":"Stara wersja",')]
    versions = versions[versions.index('}],') + len('}],'):]
    versionStart = versions.index('"obj":') + len('"obj":')
    version = versions[versionStart: versions.index('}', versionStart)]
    log.info('Nowa wersja planu to: ' + str(version))

    ##################################################
    # Pozyskanie gpid, gsh i phpsessid
    ##################################################
    gpid_start = serverResponse.index('gpid=') + 5
    gsh_start = serverResponse.index('gsh=') + 4
    gpid = serverResponse[gpid_start: serverResponse.index('&', gpid_start)]
    gsh = serverResponse[gsh_start: serverResponse.index('"', gsh_start)]

    cookie = serverResponseOrig.getheader('Set-Cookie')
    cookie = cookie[cookie.index('PHPSESSID=') + 10: cookie.index(';')]

    ##################################################
    # Pobranie planu
    ##################################################
    params = {'gpid': gpid,
              'gsh': gsh,
              'action': 'switch',
              '_LJSL': '4100',
              'num': version}
    ret = url_request('https://lo3gdynia.edupage.org/gcall',
                      {'Cookie': 'PHPSESSID=' + cookie},
                      params).read().decode('UTF-8')

    begin = ret.index('app.Sync(') + len('app.Sync(')
    end = ret.index(');', begin)
    return StringIO(ret[begin:end])


def updateTimeTables():
    if not os.path.exists(CACHE_LOCATION + 'timetables'):
        os.makedirs(CACHE_LOCATION + 'timetables')

    _gcall = download_gcall()
    tb = TimeTableDB(json.load(_gcall))

    singular = {'classes': 'class', 'students': 'student', 'classrooms': 'classroom',
                'teachers': 'teacher'}
    for object_type in ['classes', 'classrooms', 'teachers']:
        for object_id in load_ids(object_type).values():
            with open(CACHE_LOCATION + 'timetables/' + singular[object_type] +
                      object_id.replace('*', '#') + '.tt', 'wb') as f:
                pickle.dump(tb.getTimeTableForObject(singular[object_type], object_id), f, 2)

    ##################################################
    # Specjalne traktowanie niesfornych uczniów
    ##################################################
    students = load_ids('students')
    for obj_class in students:
        for student in students[obj_class]:
            with open(CACHE_LOCATION + 'timetables/student' + student['id'].replace('*', '#') + '.tt', 'wb') as f:
                pickle.dump(tb.getTimeTableForObject('student', student['id']), f, 2)


##################################################
# Generowanie dla klienta
##################################################
def verifyInput(selector, uid):
    """Check correctness of given selector and ID"""
    if selector is None or uid is None:
        raise TimeTableException('Nie podano selecktora, bądź identyfikatora')
    if selector not in ['class', 'classroom', 'student', 'teacher']:
        raise TimeTableException('Podano błędny selektor')
    if not re.match(r'^[*-]?\d{1,3}$', uid):
        raise TimeTableException('Podano błędny identyfikator')


def loadTimeTable(selector, uid):
    verifyInput(selector, uid)
    if not os.path.exists(CACHE_LOCATION + 'timetables'):
        os.makedirs(CACHE_LOCATION + 'timetables')
    try:
        with open(CACHE_LOCATION + 'timetables/' + selector + uid.replace('*', '#') + '.tt', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        if DEBUG:
            log.info('DEBUG mode active - downloading timetable')
            updateTimeTables()
            raise TimeTableException('Tryb debugowania jest aktywny. Pobrano plany lekcji. Odśwież stronę.')
        else:
            raise TimeTableException('Żądany plan lekcji nie istnieje')


def getSelectorName(selector):
    return {'class': 'Klasa', 'student': 'Uczeń', 'teacher': 'Nauczyciel', 'classroom': 'Sala'}.get(selector, '')


def getPluralName(selector):
    return {'class': 'classes', 'student': 'students',
            'teacher': 'teachers', 'classroom': 'classrooms'}.get(selector, '')


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
    try:
        a = Alias.objects.get(orig=c, selector=sel)
        return a.alias
    except ObjectDoesNotExist:
        return c


##################################################
# Klasy
##################################################
class TimeTableDB:
    def __init__(self, _db):
        self.database = _db

        self.studentsList = {i['id']: i for i in self.database['changes'][self.getTablePosition('students')]['rows']}
        self.teachersList = {i['id']: i for i in self.database['changes'][self.getTablePosition('teachers')]['rows']}
        self.classroomsList = {i['id']: i for i in self.database['changes'][self.getTablePosition('classrooms')]['rows']}
        self.subjectsList = {i['id']: i for i in self.database['changes'][self.getTablePosition('subjects')]['rows']}
        self.classesList = {i['id']: i for i in self.database['changes'][self.getTablePosition('classes')]['rows']}
        self.daysList = {i['id']: i for i in self.database['changes'][self.getTablePosition('daysdefs')]['rows']}
        self.groupsList = {i['id']: i for i in self.database['changes'][self.getTablePosition('groups')]['rows']}
        self.studentsSubjectsList = {i['id']: i for i in self.database['changes'][self.getTablePosition('studentsubjects')]['rows']}

        self.cards = self.database['changes'][self.getTablePosition('cards')]['rows']
        self.lessons = {i['id']: i for i in self.database['changes'][self.getTablePosition('lessons')]['rows']}

        self.daysNameList = {'0': 'Poniedziałek', '1': 'Wtorek', '2': 'Środa',
                             '3': 'Czwartek', '4': 'Piątek', '5': 'Sobota', '6': 'Niedziela'}

    def getTimeTableForObject(self, object_type, object_id):
        """Generate timetable

        :param object_type: Type of object - [class, teacher, classroom]
        :param object_id: Object ID
        :return: Array representing timetable
        """
        timetable = {i: [[] for _ in range(0, 18)] for i in list(self.daysNameList.values())}
        timetable['timetable_settings'] = {'begin': 0, 'end': 14, 'is_saturday': True}
        for card in self.cards:
            lesson = self.getLesson(card['lessonid'])
            if self.filterCards(lesson, object_type, object_id, card):
                period = card.get('period')
                day = str(self.getDays(card.get('days')).get('val', ''))
                if period == '' or day == '':
                    continue

                duration = lesson.get('durationperiods')
                classes = ' '.join([getAliasOfClass(self.getClass(i)['name']) for i in lesson['classids']])
                teachers = ' '.join([self.getTeacherName(i)for i in lesson['teacherids']])
                classrooms = ' '.join([self.getClassroom(i).get('name', '') for i in card['classroomids']])

                subject = self.getSubject(lesson['subjectid'])
                color = subject.get('color')
                color = get_color(subject['name'], color)
                subject = getAliasOfSubject(subject['name'])

                cell_object = {'classes': classes,
                               'teacher': teachers,
                               'classroom': classrooms,
                               'subject': subject,
                               'color': color}
                for shift in range(0, duration):
                    timetable[self.daysNameList.get(day, '0')][int(period) + shift].append(cell_object)
        timetable['timetable_settings']['is_saturday'] = not self.checkIfSaturdayIsEmpty(timetable['Sobota'])
        timetable['timetable_settings']['begin'] = self.checkIfZeroLessonNotExist(timetable)
        timetable['timetable_settings']['end'] = self.getLessonsEnding(timetable)
        return timetable

    def filterCards(self, lesson, object_type, object_id, card):
        if object_type == 'class':
            return True if object_id in lesson['classids'] else False
        elif object_type == 'teacher':
            return True if object_id in lesson['teacherids'] else False
        elif object_type == 'classroom':
            return True if object_id in card.get('classroomids', []) else False
        elif object_type == 'student':
            id_class = self.getStudent(object_id).get('classid', '')
            if id_class not in lesson.get('classids'):
                return False

            for group in lesson.get('groupids', []):
                group_item = self.getGroup(group)
                if group_item.get('classid', '') == id_class and group_item.get('entireclass', True):
                    return True

            if lesson.get('subjectid', '') in self.getStudentsSubjects(object_id) \
                    and lesson.get('seminargroup') in self.getStudentsGroups(object_id, lesson.get('subjectid', '')):
                return True
            else:
                return False
        else:
            return False

    def getTablePosition(self, table_name):
        """Return index for given table name"""
        for idx, position in enumerate(self.database['changes']):
            if position['table'] == table_name:
                return idx

    def getStudent(self, _id):
        return self.studentsList.get(_id, {})

    def getTeacher(self, _id):
        return self.teachersList.get(_id, {})

    def getTeacherName(self, _id):
        teacher = self.teachersList.get(_id, {})
        return self.GetListElement(teacher.get('firstname', ''), 0, '') + '. ' + teacher.get('lastname')

    def getClassroom(self, _id):
        return self.classroomsList.get(_id, {})

    def getSubject(self, _id):
        return self.subjectsList.get(_id, {})

    def getClass(self, _id):
        return self.classesList.get(_id, {})

    def getLesson(self, _id):
        return self.lessons.get(_id, {})

    def getGroup(self, _id):
        return self.groupsList.get(_id, {})

    def getStudentsSubjects(self, _id):
        ret = []
        for key in self.studentsSubjectsList:
            if self.studentsSubjectsList[key].get('studentid', '') == _id:
                ret.append(self.studentsSubjectsList[key].get('subjectid', ''))
        return ret

    def getStudentsGroups(self, _id, _subjectid):
        ret = []
        for key in self.studentsSubjectsList:
            if self.studentsSubjectsList[key].get('studentid', '') == _id and \
                    self.studentsSubjectsList[key].get('subjectid', '') == _subjectid:
                ret.append(self.studentsSubjectsList[key].get('seminargroup', ''))
        return ret

    @staticmethod
    def GetListElement(l, element, default):
        try:
            return l[element]
        except IndexError:
            return default

    def getDays(self, _binary):
        if _binary == '':
            return {}
        b = int(_binary, 2)
        for day in self.daysList:
            if len(self.daysList[day]['vals']) == 1 and \
                    b == int(self.daysList[day]['vals'][0], 2):
                return self.daysList[day]
        return {}

    def checkIfSaturdayIsEmpty(self, saturday):
        for cell in saturday:
            if cell:
                return False
        return True

    def checkIfZeroLessonNotExist(self, timetable):
        for day in timetable:
            if day != 'timetable_settings':
                if timetable[day][0]:
                    return 0
        return 1

    def getLessonsEnding(self, timetable):
        biggest_num = 6
        for day in timetable:
            if day == 'timetable_settings':
                continue
            iterator = len(timetable[day]) - 1
            while iterator >= 0:
                if timetable[day][iterator]:
                    break
                iterator -= 1
            if biggest_num < iterator:
                biggest_num = iterator
        return biggest_num


class TimeTableException(Exception):
    def __init__(self, message):
        self.message = message
