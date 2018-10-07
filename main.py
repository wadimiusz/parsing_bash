import datetime
import requests
from argparse import ArgumentParser
from bs4 import BeautifulSoup


class Quote(object):
    def __init__(self, number: int, text: str, date: datetime.date, rated: int):
        if not isinstance(number, int):
            raise TypeError("number must be int, not", type(number))

        if not isinstance(text, str):
            raise TypeError("text must be str, not", type(text))

        if not isinstance(date, datetime.date):
            raise TypeError("date must be datetime.date, not", type(date))

        if not isinstance(rated, int):
            raise TypeError("rated must be int, not", type(rated))

        self.number = number
        self.text = text
        self.date = date
        self.rated = rated

    def __str__(self) -> str:
        return "Цитата №{number} от {date} с рейтингом {rated}\n"\
               "{text}\n"\
               "==================================================".format(
                number=self.number, date=self.date,
                rated=self.rated, text=self.text)

    def __repr__(self) -> str:
        return "Quote #{number} from {date}, rated {rated}".format(
            number=self.number, date=self.date, rated=self.rated
        )


class PageIterator(object):
    def __init__(self):
        answer = requests.get('https://bash.im')
        if answer.status_code != 200:
            raise ValueError("Status code is {n}, not 200, probably some connection error".format(
                n=answer.status_code
            ))
        text = answer.text
        soup = BeautifulSoup(text)
        if len(soup.findAll('div', {"class": "pager"})) == 2:
            pager = soup.findAll('div', {"class": "pager"})[0]
        else:
            raise ValueError("must be two pagers, not", len(soup.findAll('div', {"class": "pager"})))

        if len(pager.findAll('input')) == 1:
            self.max = int(pager.findAll('input')[0].attrs['max'])
            self.min = int(pager.findAll('input')[0].attrs['min'])
        else:
            raise ValueError("Expected 1 input in pager, not", len(pager.findAll('input')))

        self.i = self.max + 1

    def __iter__(self):
        return self

    def __next__(self) -> BeautifulSoup:
        if self.i >= 1:
            self.i -= 1
            text = requests.get("https://bash.im/index/{num}".format(
                num=self.i
            )).text
            soup = BeautifulSoup(text)
            return soup
        else:
            raise StopIteration


class QuoteIterator(object):
    def __init__(self):
        self.page_iter = PageIterator()
        self.queue = list()

    def __iter__(self):
        return self

    def __next__(self) -> Quote:
        if len(self.queue) == 0:
            page = next(self.page_iter)
            quotes = page.findAll('div', {"class": "quote"})
            self.queue = quotes

        current_quote = self.queue.pop(0)
        text = current_quote.findAll('div', {'class': 'text'})[0].get_text()
        datetimetext = current_quote.findAll('span', {'class': 'date'})[0].text
        date = datetime.datetime.strptime(datetimetext, '%Y-%m-%d %H:%M').date()
        number = int(current_quote.findAll('a', {"class": "id"})[0].text[1:])
        rated = current_quote.findAll("span", {"class": "rating"})[0].text
        if rated == ' ... ':
            rated = -1
        else:
            rated = int(rated)

        next_quote = Quote(number=number, text=text, date=date, rated=rated)

        return next_quote


def get_range(date_from: datetime.date, date_to: datetime.date):
    quote_iter = QuoteIterator()
    for quote in quote_iter:
        if quote.date < date_from:
            break
        elif quote.date > date_to:
            pass
        else:
            yield quote

def main():
    parser = ArgumentParser()
    parser.add_argument('-df', '--date_from', dest='date_from', type=str, default="2018-08-01",
                        help="The first day of the range from which to "
                             "extract quotes. Must be in format yyyy-mm-dd")

    parser.add_argument('-dt', '--date_to', dest='date_to', type=str, default="2018-08-31",
                        help="The last day of the range from which to "
                             "extract quotes. Must be in format yyyy-mm-dd")

    parser.add_argument('-o', '--output', dest='output', type=str, default="output.txt",
                        help="The path to the file where to store the quotes.")

    args = parser.parse_args()
    date_from = datetime.datetime.strptime(args.date_from, '%Y-%m-%d').date()
    date_to = datetime.datetime.strptime(args.date_to, '%Y-%m-%d').date()
    output = args.output

    with open(output, encoding='utf-8', mode='w') as f:
        for quote in get_range(date_from, date_to):
            f.write(str(quote) + '\n')

if __name__ == '__main__':
    main()