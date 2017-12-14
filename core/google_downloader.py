import os
import sys
import urllib
import urlparse

from lxml import etree
import requests


class GoogleDownloader(object):
    REQUEST_URL = 'http://www.google.ca/search'

    @staticmethod
    def search_paper_file(paper_name):
        url = '{googlesearch_url}?{query}'.format(
            googlesearch_url=GoogleDownloader.REQUEST_URL,
            query=urllib.urlencode({'q': paper_name})
        )
        response = requests.get(url)
        if response.status_code != 200:
            print >>sys.stderr, 'Google unaccessible'
            return []

        possible_pdfs = []
        root = etree.HTML(response.text)
        h3_elements = root.xpath("//h3[contains(@class, 'r')]")
        for h3_element in h3_elements:
            link = h3_element.getchildren()[0]
            link_text = ''.join(link.itertext())
            link_contents = link.get('href')
            if link_contents.startswith('/url?q'):
                query_for_link = urlparse.parse_qs(link_contents)
                link_url = query_for_link['/url?q'][0]
                if link_url.endswith('.pdf'):
                    possible_pdfs.append((link_text, link_url))
                elif 'arxiv.org/abs' in link_url:
                    parse_result = urlparse.urlparse(link_url)
                    abs, paper_id = os.path.split(parse_result.path)
                    pdf_result = urlparse.ParseResult(
                        parse_result.scheme,
                        parse_result.netloc,
                        '/pdf/' + paper_id,
                        '', '', '')
                    pdf_url = urlparse.urlunparse(pdf_result)
                    possible_pdfs.append((link_text, pdf_url))
        return possible_pdfs
