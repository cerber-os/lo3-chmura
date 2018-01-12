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
    with open(get_cur_path() + '/agentaF/agenta.ag', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict():
    try:
        with open(get_cur_path() + '/agentaF/agenta.ag', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        agenta = download_agenta()
        save_dict(agenta)
        return agenta


def get_agenta():
    return load_dict()


def download_agenta():
    url = urllib.request.Request('http://lo3.gdynia.pl/organizacja/page-55')
    web = urllib.request.urlopen(url)

    web = web.read().decode('UTF-8')
    web = web.replace('<B>', '')
    web = web.replace('</B>', '')
    web = StringIO(web)

    page = BeautifulSoup(web, 'html5lib')

    table = page.find('table', attrs={'cols': '3', 'frame': 'VOID', 'cellspacing': '0'}).find('tbody').find_all('tr')

    agenta = []

    for row in table:
        copy_row = []
        cols = row.find_all('td')
        for col in cols:
            copy_row.append(col.get_text().replace('\n', ''))
        agenta.append(copy_row)

    return agenta


def agentaJob():
    agenta = download_agenta()
    save_dict(agenta)
