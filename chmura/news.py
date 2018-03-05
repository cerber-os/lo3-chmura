from bs4 import BeautifulSoup
from .utils import url_request
from lo3.settings import DEBUG, CACHE_LOCATION
from django.http import Http404
import pickle
import chmura.log as log
import os


def save_dict(obj):
    if not os.path.exists(CACHE_LOCATION + 'newsF'):
        os.makedirs(CACHE_LOCATION + 'newsF')
    with open(CACHE_LOCATION + 'news.nw', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict():
    if not os.path.exists(CACHE_LOCATION + 'newsF'):
        os.makedirs(CACHE_LOCATION + 'newsF')
    try:
        with open(CACHE_LOCATION + 'news.nw', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        if DEBUG:
            log.info('Downloading news')
            news = download_news()
            save_dict(news)
        else:
            raise Http404
    return news


def download_news():
    # Te wiadomości pomijaj:
    exceptList = ['Użytkownicy mobilni', 'Plan Lekcji i Zastępstwa', 'Nasza nowa strona!', 'Aktualizacja danych']

    page = url_request('https://lo3gdynia.edupage.org/news/')
    base = BeautifulSoup(page, 'html.parser')

    news = base.find('ul', attrs={'id': 'nw_newsUl'})
    aktualnosci = []
    for message in news:
        akt = {'title': '',
               'inner': ''}
        title = message.find('span', attrs={'class': 'gadgetTitle'}, recursive=True)
        if title is not None:
            akt['title'] = title.get_text()
            if akt['title'] in exceptList:
                continue

        inner = message.find('div', attrs={'class': 'plainText'}, recursive=True)
        akt['inner'] = inner.decode_contents(formatter='html')

        aktualnosci.append(akt)

    return aktualnosci


def get_news():
    return load_dict()


def newsJob():
    log.info('Updating news')
    news = download_news()
    save_dict(news)
