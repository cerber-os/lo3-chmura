from bs4 import BeautifulSoup
from io import StringIO
from lo3.settings import DEBUG, CACHE_LOCATION
from .utils import url_request
import chmura.log as log
import pickle
import html5lib
import os


def save_dict(obj):
    if not os.path.exists(CACHE_LOCATION + 'agendaF'):
        os.makedirs(CACHE_LOCATION + 'agendaF')
    with open(CACHE_LOCATION + 'agendaF/agenda.ag', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict():
    if not os.path.exists(CACHE_LOCATION + 'agendaF'):
        os.makedirs(CACHE_LOCATION + 'agendaF')
    try:
        with open(CACHE_LOCATION + 'agendaF/agenda.ag', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        if DEBUG:
            agendaF = download_agenda()
            save_dict(agendaF)
            return agendaF
        else:
            raise AgendaException('Terminarz jest niedostępny')


def getAgenda():
    return load_dict()


def download_agenda():
    web = url_request('http://lo3.gdynia.pl/organizacja/page-55')

    web = web.read().decode('UTF-8')
    web = web.replace('<B>', '')
    web = web.replace('</B>', '')
    web = StringIO(web)

    page = BeautifulSoup(web, 'html5lib')

    table = page.find('table', attrs={'cols': '3', 'frame': 'VOID', 'cellspacing': '0'}).find('tbody').find_all('tr')

    agenda = []

    for row in table:
        copy_row = []
        cols = row.find_all('td')
        for col in cols:
            copy_row.append(col.get_text().replace('\n', ''))
        agenda.append(copy_row)

    return agenda


def updateAgenda():
    log.info('Rozpoczynam aktualizację terminarza')
    agenda = download_agenda()
    save_dict(agenda)
    log.info('Zaktualizowano terminarz')


class AgendaException(Exception):
    def __init__(self, message):
        self.message = message
