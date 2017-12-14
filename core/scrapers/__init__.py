
from .cvpr2016 import Cvpr2016Scraper


scraper_by_name = {
    'cvpr2016': Cvpr2016Scraper,
}


class UnknownScraperError(KeyError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '"{0}": unknown scraper'.format(self.name)


def create_scraper_by_type(scraper_type):
    scraper_cls = scraper_by_name.get(scraper_type)
    if None is scraper_cls:
        raise UnknownScraperError(scraper_type)
    scraper = scraper_cls()
    return scraper
