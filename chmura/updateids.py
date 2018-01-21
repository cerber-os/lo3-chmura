import urllib.request
import urllib.parse
from io import StringIO
import json
import pickle
import os
import re


def get_cur_path():
    return os.path.dirname(os.path.abspath(__file__))


def save_dict(name, obj):
    with open(get_cur_path() + '/ids/' + name + '.id', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict(name):
    try:
        with open(get_cur_path() + '/ids/' + name + '.id', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        save_ids(download_ids())
        return "null"


def download_ids():
    fragments = {'classrooms': {'start': '{"table":"classrooms","rows":[', 'end': '{"table":"teachers","rows":['},
                 'teachers': {'start': '{"table":"teachers","rows":[', 'end': '{"table":"classes","rows":['},
                 'classes': {'start': '{"table":"classes","rows":[', 'end': '{"table":"subjects","rows":['},
                 'subjects': {'start': '{"table":"subjects","rows":[', 'end': '{"table":"groups","rows":['},
                 'groups': {'start': '{"table":"groups","rows":[', 'end': '{"table":"students","rows":['},
                 'students': {'start': '{"table":"students","rows":[', 'end': '{"table":"lessons","rows":['},
                 }

    url = urllib.request.Request('https://lo3gdynia.edupage.org/timetable/')
    serverResponse = urllib.request.urlopen(url).read().decode('UTF-8')
    ids = {}

    for fragment in fragments:
        field = fragments[fragment]
        value = serverResponse[serverResponse.index(field['start']) + len(field['start']) - 1:
                               serverResponse.index(field['end'])-2]
        ids[fragment] = json.load(StringIO(value))

    return ids


def get_fields(typ, obj):
    if typ in ['teachers', 'students']:
        return obj['lastname'] + ' ' + obj['firstname']
    elif typ in ['classes', 'groups', 'classrooms']:
        return obj['name']
    else:
        return 'None'


def save_ids(ids):
    for i in ids:
        d = {}
        if i == 'students':
            continue
        for t in ids[i]:
            d[get_fields(i, t)] = t['id']
        if i == 'teachers':
            save_dict(i, dict(sorted(d.items())))
        else:
            save_dict(i, d)

    # Specjalne traktowanie elitarnych uczniów
    klasy_org = load_ids('classes')
    klasy = {v: k for k, v in klasy_org.items()}
    if 'students' in ids:
        d = {}
        for uczen in ids['students']:
            nazwisko = re.search(r'(?<=[.[|])([A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ]+)', uczen['lastname'])
            nazwisko = nazwisko.group(0) if nazwisko is not None else ""
            d.setdefault(klasy.get(uczen['classid'], '0'), []).append({'firstname': uczen['firstname'],
                                                                       'lastname': nazwisko,
                                                                       'id': uczen['id']})
        save_dict('students', d)


def load_ids(typ):
    if typ == 'breaks':
        return ["7<sup>45</sup> - 8<sup>30</sup>",
                "8<sup>40</sup> - 9<sup>25</sup>",
                "9<sup>35</sup> - 10<sup>20</sup>",
                "10<sup>30</sup> - 11<sup>15</sup>",
                "11<sup>25</sup> - 12<sup>10</sup>",
                "12<sup>30</sup> - 13<sup>15</sup>",
                "13<sup>25</sup> - 14<sup>10</sup>",
                "14<sup>25</sup> - 15<sup>10</sup>",
                "15<sup>15</sup> - 16<sup>00</sup>",
                "16<sup>05</sup> - 16<sup>50</sup>",
                ]
    return load_dict(typ)


def updateid():
    save_ids(download_ids())

