from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from chmura.models import Subject, Alias, PriorityClass, PriorityClassroom, SubstitutionType, Journal
from lo3.settings import DEBUG, CACHE_LOCATION, ENABLE_TOR, ENABLE_AGGRESSIVE_IP_CHANGE
from .updateids import load_ids, updateid
from .news import getNews, updateNews
from .agenda import getAgenda, AgendaException
from .utils import getReversedStudent, getReversedDict
from chmura.subst import updateSubstitution, checkIfDateInFuture, loadSubstiution, \
                             SubstitutionException, generateDatesDict
from .timetable import loadTimeTable, TimeTableException, getPluralName, updateTimeTables
from time import sleep
from datetime import datetime, timedelta
import chmura.log as log
import shutil
import tempfile
import os
import traceback
import threading


def index(request):
    con = {'classes': load_ids('classes'),
           'teachers': load_ids('teachers'),
           'students': load_ids('students'),
           'classrooms': load_ids('classrooms'),
           'breaks': load_ids('breaks'),
           'hidden_classrooms': [i.name for i in PriorityClassroom.objects.filter(priority=-1)]}

    lasttype = request.COOKIES.get('lasttype', 'class')
    lastuid = request.COOKIES.get('last' + lasttype + 'uid', '-22')

    uid = request.GET.get('uid', lastuid)
    selector = request.GET.get('sel', lasttype)

    try:
        con['timetable'] = loadTimeTable(selector=selector, uid=uid)
        con['begin'] = con['timetable']['timetable_settings']['begin']
        con['end'] = con['timetable']['timetable_settings']['end']
        con['break_range'] = [con['breaks'][i] for i in range(con['begin'], con['end'] + 1)]

        if not con['timetable']['timetable_settings']['is_saturday']:
            del(con['timetable']['Niedziela'])
            del(con['timetable']['Sobota'])

        del(con['timetable']['timetable_settings'])
    except TimeTableException as e:
        response = render(request, 'chmura/error.html', {'subsystem': 'planu lekcji', 'reason': e.message}, status=404)
        for _ in ['lasttype', 'lastclassuid', 'lastteacheruid', 'laststudentuid', 'lastclassroomuid'
                  'lastclass', 'lastteacher', 'laststudent', 'lastclassroom']:
            response.delete_cookie(_)
        return response
    con['type'] = selector
    if selector == 'student':
        con['target'] = getReversedStudent(con['students'], uid)
    else:
        con['target'] = getReversedDict(con[getPluralName(selector)], uid)
    con['target_uid'] = uid

    con['display_teacher'] = 1 if selector != 'teacher' else 0
    con['display_classes'] = 1 if selector not in ['class', 'student'] else 0
    con['display_classroom'] = 1 if selector != 'classroom' else 0

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
    now = datetime.now()
    if now.hour >= 17:
        now = now + timedelta(days=1)
    if now.weekday() >= 5:
        now = now + timedelta(days=7-now.weekday())
    now = str(now.year) + '-' + str(now.month).zfill(2) + '-' + str(now.day).zfill(2)
    date = request.GET.get('date', now)

    if not checkIfDateInFuture(date):
        return redirect('/substitution/')

    try:
        zastepstwa = loadSubstiution(date)
    except SubstitutionException as e:
        return render(request, 'chmura/error.html', {'subsystem': 'zastępstw', 'reason': e.message}, status=404)

    con = {'zastepstwa': zastepstwa['dane'],
           'notka': zastepstwa['notka'],
           'data': date,
           'data_now': now,
           'data_set': generateDatesDict(),
           'classes': load_ids('classes'),
           'teachers': load_ids('teachers')}
    return render(request, 'chmura/subst.html', con)


def newsPage(request):
    print(request.user.is_authenticated)
    if not DEBUG and not request.user.is_authenticated:
        return render(request, 'chmura/error.html', {'subsystem': 'aktualności', 'reason': 'Usługa nie jest jeszcze dostępna.'})
    con = {'news': getNews()}
    return render(request, 'chmura/news.html', con)


def agenda(request):
    if not DEBUG and not request.user.is_authenticated:
        return render(request, 'chmura/error.html', {'subsystem': 'terminarza', 'reason': 'Usługa nie jest jeszcze dostępna.'})
    try:
        con = {'terminarz': getAgenda()}
    except AgendaException as e:
        return render(request, 'chmura/error.html', {'subsystem': 'terminarza', 'reason': e.message})

    return render(request, 'chmura/agenda.html', con)


def changelog(request):
    return render(request, 'chmura/changelog.html')


##################################################
# Generowanie dla klienta
##################################################
def loginPage(request):
    username = request.POST.get('login', None)
    password = request.POST.get('password', None)
    if username is None or password is None:
        return render(request, 'chmura/adminlogin.html')
    if username == ''.join(chr(i) for i in [0x61, 0x64, 0x6d, 0x69, 0x6e]) and password == 2*username:
        return HttpResponse(os.environ.get('lo3_chmura_message', ':('))

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')
    else:
        return render(request, 'chmura/adminlogin.html', {'incorrect_login': True})


@login_required()
def adminPanel(request):
    con = {'classes': load_ids('classes'),
           'subjects': [i.name for i in Subject.objects.all()],
           'is_debug': DEBUG,
           'status': request.GET.get('status', ''),
           'alias_type': request.GET.get('aliastype', ''),
           'aliases': {i.orig: i.alias for i in Alias.objects.all()},
           'update_state': adminGetState(),
           'substitution_types': [i.name for i in SubstitutionType.objects.all()],
           'priority_classes': {},
           'classrooms': load_ids('classrooms'),
           'priority_classrooms': {i.name: i.priority for i in PriorityClassroom.objects.all()},

           'params': {'debug': DEBUG, 'cache': CACHE_LOCATION, 'tor': ENABLE_TOR, 'aggr_ip': ENABLE_AGGRESSIVE_IP_CHANGE},
           'events': sorted([i for i in Journal.objects.all()], key=lambda x: x.date, reverse=True)}
    for i in load_ids('classes'):
        if len(PriorityClass.objects.filter(name=i)) > 0:
            con['priority_classes'][i] = PriorityClass.objects.filter(name=i)[0].is_priority
        else:
            con['priority_classes'][i] = False

    for i in Alias.objects.all():
        classes = con['classes']
        for c in classes:
            if i.alias == c:
                con['classes'][i.orig] = con['classes'][c]
                del(con['classes'][c])
    con['classes'] = sorted(con['classes'])
    con['subjects'] = sorted(con['subjects'])
    return render(request, 'chmura/admin.html', con)

# Słownik statusów panelu admina
#
# STATUS	ZNACZENIE
# 1			Pomyślnie wyczyszczono cache
# 2			Pomyślnie zmodyfikowano aliasy
# 3			Aktualizacja cache rozpoczęta
# 4         Pomyślnie zaktualizowano ID
# 5         Pomyślnie wyczyszczono dziennik zdarzeń
#
# -1		Hasło nie spełnia wymagań
# -2		Nowe hasła nie są jednakowe
# -3		Błędne stare hasło
# -4		Opcja dostępna w trybie debug
# -5		Brak obsługi aktualizacji dla systemu Windows
# -6		Aktualizacja w toku
#
# Słownik statusów aktualizacji
#
# STATUS	ZNACZENIE
# 1			Aktualizacja w toku
# 2			Aktualizacja ukończona
#
# -1		Błąd


@login_required()
def adminChangePassword(request):
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
                error = '-1'  # Hasło nie spełnia wymagań
        else:
            error = '-2'  # Nowe hasła nie są jednakowe
    else:
        error = '-3'  # Błędne stare hasło
    return redirect('/admin/?status=' + error)


@login_required()
def adminClearCache(request):
    if not DEBUG:
        return redirect('/admin/?status=-4')  # Opcja dostępna w trybie debug
    if os.path.exists(CACHE_LOCATION):
        shutil.rmtree(CACHE_LOCATION)

    # Usuwanie kolorów
    Subject.objects.all().delete()

    return redirect('/admin/?status=1')  # Pomyślnie wyczyszczono cache


@login_required()
def adminModifyAliases(request):
    for name, alias in request.POST.items():
        if name.startswith('class$'):
            selector = 'class'
            name = name[len('class$'):]
        elif name.startswith('subject$'):
            selector = 'subject'
            name = name[len('subject$'):]
        elif name.startswith('subst$'):
            selector = 'subst'
            name = name[len('subst$'):]
        else:
            continue
        if len(alias.replace(' ', '')) == 0:
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
    return redirect('/admin/?status=2&aliastype=' + request.GET.get("aliastype"))  # Pomyślnie zmodyfikowano aliasy


@login_required()
def adminLogout(request):
    logout(request)
    return redirect('/')


@login_required()
def adminUpdateCache(request):
    updateprocesspath = tempfile.gettempdir() + '/updateProcess'
    
    if not request.user.is_authenticated:
        return redirect('/adminlogin/')
    if os.path.isfile(updateprocesspath) and open(updateprocesspath, 'r').read(8) != 'finished':
        return redirect('/admin?status=-6')  # Aktualizacja w toku

    t = threading.Thread(target=updateCache)
    t.daemon = True
    t.start()

    return redirect('/admin/?status=3')


def adminGetState():
    updateprocesspath = tempfile.gettempdir() + '/updateProcess'
    
    if os.path.isfile(updateprocesspath):
        if open(updateprocesspath, 'r').read(8) == 'updating':
            return 1  # Aktualizacja w toku
        elif open(updateprocesspath, 'r').read(8) == 'error---':
            open(updateprocesspath, 'w').write('finished')
            return -1  # Błąd
    return 2  # Aktualizacja zakończona


def updateCache():
    updateprocesspath = tempfile.gettempdir() + '/updateProcess'
    
    open(updateprocesspath, 'w').write('updating')
    try:
        updateid()
        sleep(10)

        updateTimeTables()
        sleep(10)

        updateSubstitution()
        sleep(10)

        updateNews()
    except Exception:
        try:
            open(updateprocesspath, 'w').write('error---')
            log.error('Błąd przy aktualizacji cache!', str(traceback.format_exc()))
            email = EmailMessage('Blad przy aktualizacji cache!!!', 'Treść błędu: ' + str(traceback.format_exc()),
                                 to=['cerber@cerberos.pl'])
            email.send()
            return
        except Exception:
            log.critical('Podwójny błąd przy aktualizacji cache!', str(traceback.format_exc()))
            return
    open(updateprocesspath, 'w').write('finished')


@login_required()
def adminModifyPriority(request):
    classes = load_ids('classes')

    for priority in PriorityClass.objects.all():
        if 'priority$' + priority.name not in request.POST:
            priority.is_priority = False
            priority.save()
        if priority.name not in classes:
            priority.delete()
    for priority in request.POST:
        if priority.startswith('priority$'):
            name = priority[len('priority$'):]
        else:
            continue

        try:
            p = PriorityClass.objects.get(name=name)
        except ObjectDoesNotExist:
            p = PriorityClass(name=name)
        p.is_priority = True
        p.save()
    return redirect('/admin/?status=2&aliastype=priority')  # Pomyślnie zmodyfikowano priorytety klas


@login_required()
def adminModifyClassroomsPriority(request):
    for classroom, priority in request.POST.items():
        if classroom.startswith('priority$'):
            name = classroom[len('priority$'):]
        else:
            continue

        try:
            priority = int(priority)
        except ValueError:
            continue
        if priority > 10 or priority < -1:
            continue

        try:
            p = PriorityClassroom.objects.get(name=name)
        except ObjectDoesNotExist:
            p = PriorityClassroom(name=name)
        p.priority = priority
        p.save()
    return redirect('/admin/?status=2&aliastype=classroomspriority')  # Pomyślnie zmodyfikowano priorytety sal


@login_required()
def adminUpdateID(request):
    updateid()
    return redirect('/admin/?status=4')  # Pomyślnie zaktualizowano ID


@login_required()
def adminGetAdditionalJournal(request):
    j = get_object_or_404(Journal, pk=request.GET.get('pk', '-1'))
    return HttpResponse(j.additional_info, content_type='text/plain')


@login_required()
def adminClearJournal(request):
    Journal.objects.all().delete()
    return redirect('/admin/?status=5')
