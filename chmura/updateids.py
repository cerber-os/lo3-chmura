from django.core.exceptions import ObjectDoesNotExist
from io import StringIO
from chmura.models import Alias, PriorityClass, PriorityClassroom
from .utils import get_cur_path, url_request
import json
import pickle
import re
import chmura.log as log
import locale
import os

if os.name != 'nt':
    locale.setlocale(locale.LC_COLLATE, "pl_PL.UTF-8")


def save_dict(name, obj):
    with open(get_cur_path() + '/../cache/ids/' + name + '.id', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict(name):
    if not os.path.exists(get_cur_path() + '/../cache/ids'):
        os.makedirs(get_cur_path() + '/../cache/ids')
    try:
        with open(get_cur_path() + '/../cache/ids/' + name + '.id', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        log.warning('Ids file not found. Downloading new and returning "null"')
        save_ids(download_ids())
        with open(get_cur_path() + '/../cache/ids/' + name + '.id', 'rb') as f:
            return pickle.load(f)


def download_ids():
    fragments = {'classrooms': {'start': '{"table":"classrooms","rows":[', 'end': '{"table":"teachers","rows":['},
                 'teachers': {'start': '{"table":"teachers","rows":[', 'end': '{"table":"classes","rows":['},
                 'classes': {'start': '{"table":"classes","rows":[', 'end': '{"table":"subjects","rows":['},
                 'subjects': {'start': '{"table":"subjects","rows":[', 'end': '{"table":"groups","rows":['},
                 'groups': {'start': '{"table":"groups","rows":[', 'end': '{"table":"students","rows":['},
                 'students': {'start': '{"table":"students","rows":[', 'end': '{"table":"lessons","rows":['},
                 }

    serverResponse = url_request('https://lo3gdynia.edupage.org/timetable/').read().decode('UTF-8')
    ids = {}

    for fragment in fragments:
        field = fragments[fragment]
        value = serverResponse[serverResponse.index(field['start']) + len(field['start']) - 1:
                               serverResponse.index(field['end'])-2]
        ids[fragment] = json.load(StringIO(value))

    return ids


def getClass(c, sel):
    if sel == 'classes':
        sel = 'class'
    else:
        return c
    try:
        a = Alias.objects.get(orig=c, selector=sel)
        return a.alias
    except ObjectDoesNotExist:
        return c


def get_fields(typ, obj):
    if typ in ['teachers', 'students']:
        return obj['lastname'] + ' ' + obj['firstname']
    elif typ in ['classes', 'groups', 'classrooms']:
        return getClass(obj['name'], typ)
    else:
        return 'None'


def classrooms_sort(classrooms):
    first_sort = [[] for _ in range(0, 11)]
    for classroom, idx in classrooms.items():
        try:
            priority = PriorityClassroom.objects.get(name=classroom).priority
            if priority < 0:
                priority = 9
        except ObjectDoesNotExist:
            priority = 9
        first_sort[priority].append({'classroom': classroom, 'idx': idx})

    # for i in range(0, 11):
    #    first_sort[i] = sorted(first_sort[i], key=lambda x: x['classroom'].lower())

    result = {}
    for i in range(0, 11):
        for k in first_sort[i]:
            result[k['classroom']] = k['idx']

    print(result)
    return result


def save_ids(ids):
    for i in ids:
        d = {}
        group_priority = {}
        group_normal = {}
        if i == 'students':
            continue
        for t in ids[i]:
            d[get_fields(i, t)] = t['id']
        if i == 'teachers':
            save_dict(i, dict(sorted(d.items(), key=lambda x: locale.strxfrm(x[0].replace('-', 'źź')))))
        elif i == 'classes':
            for t in d:
                if PriorityClass.objects.filter(name=t).exists() and \
                   PriorityClass.objects.filter(name=t)[0].is_priority:
                    group_priority[t] = d[t]
                else:
                    group_normal[t] = d[t]
            save_dict(i, {**dict(sorted(group_priority.items(), key=lambda x: locale.strxfrm(x[0]))),
                          **dict(sorted(group_normal  .items(), key=lambda x: locale.strxfrm(x[0])))})
        elif i == 'classrooms':
            save_dict(i, classrooms_sort(d))
        else:
            save_dict(i, d)

    # Specjalne traktowanie elitarnych uczniów
    klasy_org = load_ids('classes')
    klasy = {v: k for k, v in klasy_org.items()}
    if 'students' in ids:
        d = {}
        for uczen in ids['students']:
            nazwisko = re.search(r'(?<=[.[| ])([A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ, -]+)', uczen['lastname'])
            nazwisko = nazwisko.group(0) if nazwisko is not None else ""
            nazwisko = nazwisko.replace(',', ' ')
            nazwisko = nazwisko.replace('  ', ' ')
            d.setdefault(klasy.get(uczen['classid'], '0'), []).append({'firstname': uczen['firstname'],
                                                                       'lastname': nazwisko,
                                                                       'id': uczen['id']})
        for group in d:
            d[group] = sorted(d[group], key=lambda x: locale.strxfrm(x['lastname']))
        save_dict('students', dict(sorted(d.items())))


def load_ids(typ):
    if typ == 'breaks':
        return ["7<sup>00</sup> - 7<sup>45</sup>",
                "7<sup>45</sup> - 8<sup>30</sup>",
                "8<sup>40</sup> - 9<sup>25</sup>",
                "9<sup>35</sup> - 10<sup>20</sup>",
                "10<sup>30</sup> - 11<sup>15</sup>",
                "11<sup>25</sup> - 12<sup>10</sup>",
                "12<sup>30</sup> - 13<sup>15</sup>",
                "13<sup>25</sup> - 14<sup>10</sup>",
                "14<sup>25</sup> - 15<sup>10</sup>",
                "15<sup>15</sup> - 16<sup>00</sup>",
                "16<sup>05</sup> - 16<sup>50</sup>",
                "16<sup>55</sup> - 17<sup>40</sup>",
                "17<sup>45</sup> - 18<sup>30</sup>",
                "18<sup>35</sup> - 19<sup>20</sup>",
                "19<sup>25</sup> - 20<sup>10</sup>",
                ]
    return load_dict(typ)


def updateid():
    log.info('Updating ids')
    save_ids(download_ids())
