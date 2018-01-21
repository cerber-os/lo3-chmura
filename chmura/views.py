from django.shortcuts import render
from django.http import Http404
from .timetable import get_timetable
from .subst import get_substitution
from .updateids import load_ids
from .news import get_news
from .agenda import get_agenda
import datetime
import re


def getReversedDict(dictionary, key):
    for d in dictionary:
        if dictionary[d] == key:
            return key
    return "null"


def index(request):
    con = {}
    uid = request.GET.get('uid', '-22')
    selector = request.GET.get('sel', 'trieda')

    if not re.match(r'^[*-]?\d{1,3}$', uid):
        raise Http404

    if selector == 'trieda':
        con['type'] = 'Klasa'
        con['target'] = getReversedDict(load_ids('classes'), uid)
    elif selector == 'student':
        con['type'] = 'Uczeń'
        con['target'] = 'Jan Kowalski'
    elif selector == 'ucitel':
        con['type'] = 'Nauczyciel'
        con['target'] = getReversedDict(load_ids('teachers'), uid)
    else:
        raise Http404
    con['breaks'] = load_ids('breaks')
    con['timetable'] = get_timetable(uid=uid, selector=selector)

    return render(request, 'chmura/index.html', con)


def timetableSelect(request):
    con = {'klasy': load_ids('classes'),
           'nauczyciele': load_ids('teachers'),
           'uczniowie': load_ids('students'),
           'sale': load_ids('classrooms')}
    return render(request, 'chmura/timetable_select.html', con)


def announcement(request):
    return render(request, 'chmura/announcement.html')


def substitutionList(request):
    now = datetime.datetime.now()
    now = str(now.year) + '-' + str(now.month).zfill(2) + '-' + str(now.day).zfill(2)
    date = request.GET.get('date', now)

    zastepstwa = get_substitution(date)

    con = {'zastepstwa': zastepstwa['dane'], 'notka': zastepstwa['notka'], 'data': date, 'data_now': now}
    return render(request, 'chmura/subst.html', con)


def newsPage(request):
    con = {'news': get_news()}
    return render(request, 'chmura/news.html', con)


def agenda(request):
    con = {'terminarz': get_agenda()}
    return render(request, 'chmura/agenda.html', con)
