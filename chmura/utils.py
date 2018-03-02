import os
import urllib.request
import urllib.parse
import chmura.log as log
from lo3.settings import DEFAULT_USER_AGENT, ENABLE_TOR, ENABLE_AGGRESSIVE_IP_CHANGE, DEBUG
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


if len(Settings.objects.all()) == 0:
    unikalnanazwazmiennej = Settings()
    unikalnanazwazmiennej.save()


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
    if ENABLE_AGGRESSIVE_IP_CHANGE:
        with Controller.from_port(port=14356) as controller:
            controller.authenticate(password='tojestbardzozlaszkola')
            controller.signal(Signal.NEWNYM)
        log.info('New TOR session created')


def url_request(address, header=None, params=None):
    if header is None:
        header = {}
    if params is None:
        params = {}
    prx = {'http': '127.0.0.1:9050'} if ENABLE_TOR else {}

    header['User-Agent'] = DEFAULT_USER_AGENT

    proxy_handler = urllib.request.ProxyHandler(prx)
    opener = urllib.request.build_opener(proxy_handler)

    options = urllib.parse.urlencode(params).encode('UTF-8')
    url = urllib.request.Request(address, options, headers=header)
    serverResponse = opener.open(url)
    return serverResponse
