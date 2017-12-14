import os
import sys
import urllib
import urlparse

from lxml import etree
import requests

from core.scrapers.base import BaseScraper


class Cvpr2016Scraper(BaseScraper):
    def scrape_list_of_papers(self, page_url):
        """Parses a given page and returns list of papers for CVPR 2016 conference.

        :param page_url: page url (http://cvpr2016.thecvf.com/program/main_conference)
        :return: dictionary:
            date -> dictionary:
                session type (ORAL, POSTER, SPOTLIGHT) -> dictionary:
                    section name -> list of dictionaries:
                        'authors': string representing authors,
                        'paper-name': string representing paper name
        """
        response = requests.get(page_url)
        if response.status_code != 200:
            print >>sys.stderr, 'CVF unaccessible'
            return

        papers = {}
        root = etree.HTML(response.text)
        program_headers = root.xpath("//h3[contains(@class, 'programheader')]")
        for header in program_headers:
            current_program_title = None
            current_date = None
            current_session = header.text
            current_element = header.getnext()
            while None is not current_element and current_element.tag != 'hr':
                if current_element.tag == 'h4' and current_element.get('class') == 'program-title':
                    current_program_title = current_element.text
                elif current_element.tag == 'h5' and current_element.get('class') == 'program-title':
                    current_date = current_element.text
                elif current_element.tag == 'ul':
                    authors = current_element.find('p').text.split(',')
                    first_surname = authors[0].split()[-1]
                    authors = first_surname + ' et al.' if len(authors) > 1 else first_surname
                    paper_name = ''.join(current_element.find('strong').itertext()).strip('. ')
                    papers.setdefault(current_date, {})
                    papers[current_date].setdefault(current_session, {})
                    papers[current_date][current_session].setdefault(current_program_title, [])
                    papers[current_date][current_session][current_program_title].append({
                        'authors': authors.encode('utf-8'),
                        'paper-name': paper_name.encode('utf-8')
                    })
                current_element = current_element.getnext()
        return papers





