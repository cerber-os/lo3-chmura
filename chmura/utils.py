# Chciałbym z tego miejsca podziękować Przemub'owi za naprowadzenie mnie na rozwiązanie bug'a
# Dziękuję !!!

import os
import random
import urllib.request
import urllib.parse
import chmura.log as log
from django.shortcuts import render
from lo3.settings import ENABLE_TOR, ENABLE_AGGRESSIVE_IP_CHANGE, DEBUG
from time import sleep
from chmura.models import Settings


if DEBUG:
    log.error('Debug mode is active!!! Do not use it in production!')

if ENABLE_TOR:
    log.info('TOR forwarding enabled')
else:
    log.warning('TOR not enabled!!!')

if ENABLE_AGGRESSIVE_IP_CHANGE:
    from stem import Signal
    from stem.control import Controller

    log.warning('Aggressive IP changing is active!')

USER_AGENTS_LIST = ['Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 16.0; rv:42.0) Gecko/20100101 Firefox/42.0',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 7.1; Win64; x64; rv:56.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2704.103 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
                    'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)',
                    'Mozilla/5.0 (Linux; U; Android 4.1.1; pl-pl; Build/KLP) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30',
                    'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
                    'Mozilla/5.0 (Tablet; rv:26.0) Gecko/26.0 Firefox/26.0',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4',
                    'Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko; googleweblight) Chrome/38.0.1025.166 Mobile Safari/535.19',
                    'Mozilla/5.0 (Linux; U; Android 4.4.2; pl-pl; SM-G900F Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                    'Mozilla/5.0 (Linux; U; Android 4.0.4; nl-nl; GT-N8010 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30']

CURRENT_USER_AGENT = random.choice(USER_AGENTS_LIST)


def get_cur_path():
    return os.path.dirname(os.path.abspath(__file__))


def getReversedDict(dictionary, key):
    for d in dictionary:
        if dictionary[d] == key:
            return d
    return "null"


def getReversedStudent(dictionary, key):
    for d in dictionary:
        for k in dictionary[d]:
            if k['id'] == key:
                return k['lastname'] + ' ' + k['firstname']
    return "null"


def create_new_session():
    global CURRENT_USER_AGENT
    if ENABLE_AGGRESSIVE_IP_CHANGE:
        with Controller.from_port(port=14356) as controller:
            controller.authenticate(password='tojestbardzozlaszkola')
            controller.signal(Signal.NEWNYM)
        CURRENT_USER_AGENT = random.choice(USER_AGENTS_LIST)
        log.info('New TOR session created')


def url_request(address, header=None, params=None):
    if header is None:
        header = {}
    if params is None:
        params = {}
    prx = {'http': '127.0.0.1:9050'} if ENABLE_TOR else {}

    header['User-Agent'] = CURRENT_USER_AGENT

    proxy_handler = urllib.request.ProxyHandler(prx)
    opener = urllib.request.build_opener(proxy_handler)

    options = urllib.parse.urlencode(params).encode('UTF-8')
    url = urllib.request.Request(address, options, headers=header)
    try:
        serverResponse = opener.open(url)
    except Exception:
        sleep(10)
        serverResponse = opener.open(url)
    return serverResponse


def requestedTimetableError(request, reason):
    response = render(request, 'chmura/timetableerror.html', {'reason': reason}, status=404)
    for _ in ['lasttype', 'lastclassuid', 'lastteacheruid', 'laststudentuid',
              'lastclass', 'lastteacher', 'laststudent']:
        response.delete_cookie(_)
    return response
