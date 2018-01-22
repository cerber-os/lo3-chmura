import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from io import StringIO
import os
import pickle
import html5lib


def get_cur_path():
    return os.path.dirname(os.path.abspath(__file__))


def save_dict(obj):
    with open(get_cur_path() + '/agendaF/agenda.ag', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict():
    try:
        with open(get_cur_path() + '/agendaF/agenda.ag', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        agenda = download_agenda()
        save_dict(agenda)
        return agenda


def get_agenda():
    return load_dict()


def download_agenda():
    url = urllib.request.Request('http://lo3.gdynia.pl/organizacja/page-55')
    web = urllib.request.urlopen(url)

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


def agendaJob():
    agenda = download_agenda()
    save_dict(agenda)
