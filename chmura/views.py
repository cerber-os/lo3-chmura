from django.shortcuts import render
from django.http import Http404
from .timetable import get_timetable
from .subst import get_substitution
from .updateids import load_ids
from .news import get_news
from .agenda import get_agenda
from .utils import *
import datetime
import re
import chmura.log as log
from django.shortcuts import redirect


def index(request):
    types = {'class': 'trieda',
             'student': 'student',
             'teacher': 'ucitel'}

    con = {'classes': load_ids('classes'),
           'teachers': load_ids('teachers'),
           'students': load_ids('students'),
           'classrooms': load_ids('classrooms'),
           'breaks': load_ids('breaks')}

    lasttype = request.COOKIES.get('lasttype', 'class')
    lastuid = request.COOKIES.get('last' + lasttype + 'uid', '-22')

    uid = request.GET.get('uid', lastuid)
    selector = types.get(request.GET.get('sel', lasttype))

    if not re.match(r'^[*-]?\d{1,3}$', uid):
        log.info('Incorrect uid was given')
        raise Http404

    if selector is None:
        log.info('Incorrect selector was given')
        raise Http404

    if selector == 'trieda':
        con['type'] = 'Klasa'
        con['target'] = getReversedDict(con['classes'], uid)
    elif selector == 'student':
        con['type'] = 'Uczeń'
        con['target'] = getReversedStudent(con['students'], uid)
    elif selector == 'ucitel':
        con['type'] = 'Nauczyciel'
        con['target'] = getReversedDict(con['teachers'], uid)
    else:
        raise Http404
    con['timetable'] = get_timetable(uid=uid, selector=selector)
    con['target_uid'] = uid
    begin = 0 if '0' in con['timetable']['Poniedziałek'] else 1
    con['begin'] = begin
    try:
        end = con['timetable']['Poniedziałek'].keys()
        end = [int(e) for e in end]
        end = int(sorted(end)[-1])
    except ValueError:
        end = 9
    con['break_range'] = [con['breaks'][i] for i in range(begin, end + 1)]

    if 'Chrome' in request.user_agent.browser.family:
        con['device'] = 'Chrome'
    elif 'Safari' in request.user_agent.browser.family:
        con['device'] = 'Safari'
    else:
        con['device'] = 'Other'

    return render(request, 'chmura/index.html', con)


def announcement(request):
    return render(request, 'chmura/announcement.html')


def substitutionList(request):
    now = datetime.datetime.now()
    now = str(now.year) + '-' + str(now.month).zfill(2) + '-' + str(now.day).zfill(2)
    date = request.GET.get('date', now)

    try:
        date_diff = (datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.datetime.strptime(now, '%Y-%m-%d')).days
        if date_diff < 0 or date_diff > 7:
            return redirect('/substitution/')
    except ValueError:
        return redirect('/substitution/')

    try:
        zastepstwa = get_substitution(date)
    except Http404:
        return redirect('/substitution/')

    con = {'zastepstwa': zastepstwa['dane'],
           'notka': zastepstwa['notka'],
           'data': date,
           'data_now': now,
           'classes': load_ids('classes'),
           'teachers': load_ids('teachers')}
    return render(request, 'chmura/subst.html', con)


def newsPage(request):
    con = {'news': get_news()}
    return render(request, 'chmura/news.html', con)


def agenda(request):
    con = {'terminarz': get_agenda()}
    return render(request, 'chmura/agenda.html', con)


def changelog(request):
    return render(request, 'chmura/changelog.html')
