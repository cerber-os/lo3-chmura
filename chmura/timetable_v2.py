import json
from io import StringIO


def download_gcall():
    ret = open('/tmp/dump.txt', 'r')
    ret = ret.read()
    begin = ret.index('app.Sync(') + len('app.Sync(')
    end = ret.index(');', begin)
    return StringIO(ret[begin:end])


def process_gcall():
    _gcall = download_gcall()
    database = json.load(_gcall)
    tb = TimeTableDB(database)
    return tb.getTimeTableForObject('class', '-22')

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

        self.cards = self.database['changes'][self.getTablePosition('cards')]['rows']
        self.lessons = {i['id']: i for i in self.database['changes'][self.getTablePosition('lessons')]['rows']}

    def getTimeTableForObject(self, object_type, object_id):
        """Generate timetable

        :param object_type: Type of object - [class, teacher, classroom]
        :param object_id: Object ID
        :return: Array representing timetable
        """
        timetable = {str(i): [[] for _ in range(0, 18)] for i in range(0, 4)}
        for card in self.cards:
            lesson = self.getLesson(card['lessonid'])
            if self.filterCards(lesson, object_type, object_id):
                period = card.get('period')
                day = str(self.getDays(card.get('days')).get('val', ''))
                if period == '' or day == '':
                    continue
                duration = lesson.get('durationperiods')
                classes = ' '.join([self.getClass(i)['name'] for i in lesson['classids']])
                teachers = ' '.join([self.getTeacher(i)['firstname'] + ' ' + self.getTeacher(i)['lastname'] + ', '
                                    for i in lesson['teacherids']])
                classrooms = ' '.join([self.getClassroom(i).get('name', 'n/a') for i in card['classroomids']])

                cell_object = {'classes': classes,
                               'teachers': teachers,
                               'classrooms': classrooms,
                               'subject': self.getSubject(lesson['subjectid'])['name']}
                for shift in range(0, duration):
                    timetable[day][int(period) + shift].append(cell_object)
        return timetable

    def filterCards(self, lesson, object_type, object_id):
        if object_type == 'class':
            return True if object_id in lesson['classids'] else False
        elif object_type == 'teacher':
            return True if object_id in lesson['teacherids'] else False
        elif object_type == 'classroom':
            return True if object_id in self.GetListElement(lesson['classroomidss'], 0, []) else False
        else:
            return False

    def _debug(self):
        print(str([i for i in self.database['changes'][self.getTablePosition('daysdefs')]['rows']]))
        print(self.database['changes'][self.getTablePosition('lessons')]['rows'][0])

    def getTablePosition(self, table_name):
        """Return index for given table name"""
        for idx, position in enumerate(self.database['changes']):
            if position['table'] == table_name:
                return idx

    def getStudent(self, _id):
        return self.studentsList.get(_id, {})

    def getTeacher(self, _id):
        return self.teachersList.get(_id, {})

    def getClassroom(self, _id):
        return self.classroomsList.get(_id, {})

    def getSubject(self, _id):
        return self.subjectsList.get(_id, {})

    def getClass(self, _id):
        return self.classesList.get(_id, {})

    def getLesson(self, _id):
        return self.lessons.get(_id, {})

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
