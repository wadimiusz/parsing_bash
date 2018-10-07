import unittest
import datetime
from bs4 import BeautifulSoup

from ..main import Quote, PageIterator, QuoteIterator


class TestQuote(unittest.TestCase):
    def test_init_positive01(self):
        quote = Quote(number=100, text="Я глупенький",
                      rated=-1, date=datetime.date(1996, 6, 18))

    def test_init_negative01(self):
        with self.assertRaises(TypeError):
            quote = Quote(number="100", text="Я глупенький",
                          rated=-1, date=datetime.date(1996, 6, 18))

    def test_init_negative02(self):
        with self.assertRaises(TypeError):
            quote = Quote(number=100, text=["Я", "глупенький"],
                          rated=-1, date=datetime.date(1996, 6, 18))

    def test_init_negative03(self):
        with self.assertRaises(TypeError):
            quote = Quote(number=100, text="Я глупенький",
                          rated=" ... ", date=datetime.date(1996, 6, 18))

    def test_init_negative04(self):
        with self.assertRaises(TypeError):
            quote = Quote(number=100, text="Я глупенький",
                          rated=-1, date="1996-18-06")


class TestPageIterator(unittest.TestCase):
    def test_init_positive01(self):
        page_iter = PageIterator()
        self.assertEqual(page_iter.min, 1)
        self.assertGreaterEqual(page_iter.max, 1400)
        self.assertEqual(page_iter.max + 1, page_iter.i)

    def test_next_positive01(self):
        page_iter = PageIterator()
        soup = next(page_iter)
        self.assertIsInstance(soup, BeautifulSoup)

    def test_iter_positive01(self):
        page_iter = PageIterator()
        self.assertIsInstance(page_iter.__iter__(), PageIterator)
        self.assertIs(page_iter.__iter__(), page_iter)


class TestQuoteIterator(unittest.TestCase):
    def test_init_positive01(self):
        quote_iter = QuoteIterator()
        self.assertIsInstance(quote_iter.page_iter, PageIterator)
        self.assertIsInstance(quote_iter.queue, list)
        self.assertEqual(len(quote_iter.queue), 0)

    def test_iter_positive01(self):
        quote_iter = QuoteIterator()
        self.assertIsInstance(quote_iter.__iter__(), QuoteIterator)
        self.assertIs(quote_iter.__iter__(), quote_iter)

    def test_next_positive01(self):
        quote_iter = QuoteIterator()
        quote = next(quote_iter)
        self.assertIsInstance(quote, Quote)


if __name__ == '__main__':
    unittest.main(verbosity=2)
