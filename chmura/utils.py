import os

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows; U; Win 9x 4.90; de-DE; rv:0.9.2) Gecko/20010726 Netscape6/6.1'
ENABLE_TOR = False

if ENABLE_TOR:
    # Thanks to /u/gaten
    import socks
    import socket


    def create_connection(address, timeout=None, source_address=None):
        sock = socks.socksocket()
        sock.connect(address)
        return sock


    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
    socket.socket = socks.socksocket

    # patch the socket module
    socket.socket = socks.socksocket
    socket.create_connection = create_connection

import urllib.request
import urllib.parse


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
                return k['firstname'] + ' ' + k['lastname']
    return "null"


def url_request(address, header=None, params=None):
    global DEFAULT_USER_AGENT
    if header is None:
        header = {}
    if params is None:
        params = {}

    header['User-Agent'] = DEFAULT_USER_AGENT

    options = urllib.parse.urlencode(params).encode('UTF-8')
    url = urllib.request.Request(address, options, headers=header)
    serverResponse = urllib.request.urlopen(url)
    return serverResponse
