from django.shortcuts import render
from django.http import Http404
from .timetable import get_timetable, timetableJob
from .subst import get_substitution, updateJob
from .updateids import load_ids, updateid
from .news import get_news
from .agenda import get_agenda
from .utils import *
import datetime
import re
import chmura.log as log
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from lo3.settings import DEBUG
import shutil
from chmura.models import Subject, Alias
from django.core.exceptions import ObjectDoesNotExist
import threading
from django.core.mail import EmailMessage


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
    if now.hour > 17:
        now = now + datetime.timedelta(days=1)
    now = str(now.year) + '-' + str(now.month).zfill(2) + '-' + str(now.day).zfill(2)
    date = request.GET.get('date', now)

    try:
        date_diff = (datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.datetime.strptime(now, '%Y-%m-%d')).days
        if date_diff < -1 or date_diff > 7:
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


def loginPage(request):
    username = request.POST.get('login', None)
    password = request.POST.get('password', None)
    if username is None or password is None:
        return render(request, 'chmura/adminlogin.html')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        # Zalogowany(szef_prezesa, tajnehaslo1) - jeśli sądzisz, że na produkcji są te same dane, to lepiej zmień zawód
        login(request, user)
        return redirect('/admin/')
    else:
        return render(request, 'chmura/adminlogin.html', {'incorrect_login': True})


def adminPanel(request):
    if not request.user.is_authenticated:
        return redirect('/adminlogin/')
    con = {'classes': load_ids('classes'),
           'subjects': [i.name for i in Subject.objects.all()],
           'is_debug': DEBUG,
           'error': request.GET.get('error', ''),
           'info': request.GET.get('info', ''),
           'aliases': {i.orig: i.alias for i in Alias.objects.all()},
           'update_state': adminGetState()}
    for i in Alias.objects.all():
        classes = con['classes']
        for c in classes:
            if i.alias == c:
                con['classes'][i.orig] = con['classes'][c]
                del(con['classes'][c])
    con['classes'] = sorted(con['classes'])
    con['subjects'] = sorted(con['subjects'])
    return render(request, 'chmura/admin.html', con)


def adminChangePassword(request):
    if not request.user.is_authenticated:
        return redirect('/adminlogin/')
    u = User.objects.get(username=request.user.username)
    newpassword = request.POST.get('new_password', '1')
    if u.check_password(request.POST.get('old_password', None)):
        if newpassword == request.POST.get('newer_password', '0'):
            if len(newpassword) >= 8 and any(i.isdigit() for i in newpassword):
                u.set_password(newpassword)
                u.save()
                logout(request)
                return redirect('/adminlogin/')
            else:
                error = 'Hasło jest za krótkie, bądź nie zawiera conajmniej jednej cyfry'
        else:
            error = 'Hasła nie są jednakowe'
    else:
        error = 'Wprowadzono błędne stare hasło'
    return redirect('/admin?error=' + error)


def adminClearCache(request):
    if not request.user.is_authenticated:
        return redirect('/adminlogin/')
    if not DEBUG:
        return redirect('/admin/?info=Opcja dostępna wyłącznie w trybie DEBUG')
    if os.path.exists(get_cur_path() + '/../cache'):
        shutil.rmtree(get_cur_path() + '/../cache/')

    # Usuwanie kolorów
    Subject.objects.all().delete()

    return redirect('/admin?info=' + 'Pomyślnie wyczyszczono cache')


def adminModifyAliases(request):
    if not request.user.is_authenticated:
        return redirect('/adminlogin/')

    for name, alias in request.POST.items():
        if name.startswith('class$'):
            selector = 'class'
            name = name[len('class$'):]
        elif name.startswith('subject$'):
            selector = 'subject'
            name = name[len('subject$'):]
        else:
            continue
        if len(alias) == 0 or len(alias.replace(' ', '')) == 0:
            try:
                a = Alias.objects.get(orig=name)
                a.delete()
            except ObjectDoesNotExist:
                continue
            continue

        try:
            a = Alias.objects.get(orig=name)
        except ObjectDoesNotExist:
            a = Alias(orig=name, alias=alias, selector=selector)
        a.alias = alias
        a.save()
    return redirect('/admin?info=Pomyślnie zmodyfikowano aliasy')


def adminLogout(request):
    if not request.user.is_authenticated:
        return redirect('/adminlogin/')
    logout(request)
    return redirect('/')


def adminUpdateCache(request):
    if not request.user.is_authenticated:
        return redirect('/adminlogin/')
    if os.name == 'nt':
        return redirect('/admin?info=Ta funkcja nie działa w systemie Windows')
    if os.path.isfile('/tmp/updateProcess') and open('/tmp/updateProcess', 'r').read(8) != 'finished':
        return redirect('/admin?info=Aktualizacja jeszcze trwa')

    t = threading.Thread(target=updateCache)
    t.setDaemon(True)
    t.start()

    return redirect('/admin?info=Pomyślnie rozpoczęto aktualizację cache')


def adminGetState():
    if os.path.isfile('/tmp/updateProcess'):
        if open('/tmp/updateProcess', 'r').read(8) == 'updating':
            return 'Aktualizacja w trakcie'
        elif open('/tmp/updateProcess', 'r').read(8) == 'error---':
            open('/tmp/updateProcess', 'w').write('finished')
            return 'Wystąpił błąd. Spróbuj ponownie'
    return 'Aktualizacja ukończona'


def updateCache():
    open('/tmp/updateProcess', 'w').write('updating')
    try:
        updateid()
        timetableJob()
        updateJob()
    except Exception as e:
        try:
            open('/tmp/updateProcess', 'w').write('error---')
            log.error(e)
            email = EmailMessage('Blad przy aktualizacji cache!!!', 'Treść błędu: ' + str(e), to=['cerber@cerberos.pl'])
            email.send()
        except Exception as e:
            log.crititcal('Double error!!!: ' + str(e))
            return
    open('/tmp/updateProcess', 'w').write('finished')
    return
