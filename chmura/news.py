import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import pickle
import os


def get_cur_path():
    return os.path.dirname(os.path.abspath(__file__))


def save_dict(obj):
    with open(get_cur_path() + '/news/news.nw', 'wb') as f:
        pickle.dump(obj, f, 2)


def load_dict():
    try:
        with open(get_cur_path() + '/news/news.nw', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        news = download_news()
        save_dict(news)
        return news


def download_news():
    # Te wiadomości pomijaj:
    exceptList = ['Użytkownicy mobilni', 'Plan Lekcji i Zastępstwa', 'Nasza nowa strona!', 'Aktualizacja danych']

    url = urllib.request.Request('https://lo3gdynia.edupage.org/news/')
    page = urllib.request.urlopen(url)
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
    news = download_news()
    save_dict(news)
