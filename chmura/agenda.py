from bs4 import BeautifulSoup
from io import StringIO
import pickle
import html5lib
from .utils import *
import chmura.log as log


def save_dict(obj):
    with open(get_cur_path() + '/agendaF/agenda.ag', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict():
    if not os.path.exists(get_cur_path() + '/agendaF'):
        os.makedirs(get_cur_path() + '/agendaF')
    try:
        with open(get_cur_path() + '/agendaF/agenda.ag', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        agendaF = download_agenda()
        save_dict(agendaF)
        return agendaF


def get_agenda():
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


def agendaJob():
    log.info('Updating agenda')
    agenda = download_agenda()
    save_dict(agenda)
