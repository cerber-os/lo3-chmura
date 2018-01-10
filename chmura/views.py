from django.shortcuts import render
from django.http import Http404
from .timetable import get_timetable
from .subst import get_substitution
from .updateids import load_ids
import datetime


def index(request):
    con = {}
    uid = request.GET.get('uid', '-22')
    selector = request.GET.get('sel', 'trieda')

    klasy = load_ids('classes')
    nauczyciele = load_ids('teachers')

    if selector == 'trieda':
        con['type'] = 'Klasa'
        for klasa in klasy:
            if klasy[klasa] == uid:
                con['target'] = klasa
    elif selector == 'student':
        con['type'] = 'Uczeń'
        con['target'] = 'Jan Kowalski'
    elif selector == 'ucitel':
        con['type'] = 'Nauczyciel'
        for n in nauczyciele:
            if nauczyciele[n] == uid:
                con['target'] = n
    else:
        raise Http404
    con['breaks'] = load_ids('breaks')
    con['timetable'] = get_timetable(uid=uid, selector=selector)
    return render(request, 'chmura/index.html', con)


def timetableSelect(request):
    con = {'klasy': load_ids('classes'),
           'nauczyciele': load_ids('teachers'),
           'uczniowie': load_ids('students')}
    return render(request, 'chmura/timetable_select.html', con)


def announcement(request):
    return render(request, 'chmura/announcement.html')


def substitutionList(request):
    now = datetime.datetime.now()
    now = str(now.year) + '-' + str(now.month).zfill(2) + '-' + str(now.day).zfill(2)
    date = request.GET.get('date', now)

    con = {'zastepstwa': get_substitution(date), 'data': date, 'data_now': now}
    return render(request, 'chmura/subst.html', con)
