#!/usr/bin/env python

import argparse
import hashlib
import logging
import multiprocessing as mp
import os
import shutil
import sys

import requests

__dir__ = os.path.dirname(__file__)
sys.path[1:1] = [os.path.normpath(
    os.path.join(__dir__, '..'))
]

from core.scrapers import create_scraper_by_type
from core.google_downloader import GoogleDownloader
from utils.log import setup_custom_logger


def ensure_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def download_papers(data):
    global logger
    logger = logging.getLogger('root')
    if not logger.handlers:
        logger = setup_custom_logger('root')
    base_dir, papers_by_section = data
    gd = GoogleDownloader()
    results = []
    for paper in papers_by_section:
        try:
            print paper
            folder = '{authors}_{paper-name}'.format(**paper)
            paper_dir = os.path.join(base_dir, folder)
            ensure_dir(paper_dir)
            possible_pdfs = gd.search_paper_file(paper['paper-name'])
            existing_hashes = [hashfile(open(os.path.join(paper_dir, filename), 'rb'), hashlib.md5())
                               for filename in os.listdir(paper_dir)]
            for link_text, pdf_url in possible_pdfs:
                filename = os.path.join(paper_dir, link_text + '.pdf')
                i = 1
                while os.path.exists(filename):
                    i += 1
                    filename = os.path.join(paper_dir, link_text + str(i) + '.pdf')
                print link_text
                logger.info('Downloading search result "{}" with URL {} to file "{}"'.format(
                    link_text, pdf_url, filename))
                response = requests.get(pdf_url, stream=True, verify=False)
                with open(filename, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                with open(filename, 'rb') as downloaded_file:
                    file_hash = hashfile(downloaded_file, hashlib.md5())
                if file_hash in existing_hashes:
                    os.unlink(filename)
                    logger.info('Hash of downloaded file is {} '
                                'and we already have this file; removing it'.format(file_hash))
                else:
                    existing_hashes.append(file_hash)
                    logger.info('Hash of downloaded file is {}, '
                                'adding it to folder'.format(file_hash))
                    results.append((folder, filename))
        except Exception as e:
            logger.exception('Download of paper "{}" failed'.format(folder))
    return results


def main(options):
    global logger
    logger = setup_custom_logger('root', filename=options.log_file)

    scraper = create_scraper_by_type(options.conference)
    papers = scraper.scrape_list_of_papers(options.conference_program_url)

    work_data = []
    for date, papers_by_date in papers.iteritems():
        ensure_dir(os.path.join(options.destination_dir, date))
        for session, papers_by_session in papers_by_date.iteritems():
            ensure_dir(os.path.join(options.destination_dir, date, session))
            for section, papers_by_section in papers_by_session.iteritems():
                base_dir = os.path.join(options.destination_dir, date, session, section)
                ensure_dir(base_dir)
                if not os.listdir(base_dir):
                    logger.info('Directory is empty {}, will process it'.format(base_dir))
                    work_data.append((base_dir, papers_by_section))
                else:
                    logger.info('Something is in {}, skipping it'.format(base_dir))

    # download_papers(work_data[0])

    pool = mp.Pool(8)
    for results in pool.imap_unordered(download_papers, work_data):
        for paper_name, paper_file in results:
            print paper_name
            print '  ' + paper_file
    pool.close()
    pool.join()


def parse_options():
    parser = argparse.ArgumentParser(description='Scrape the conference website and download'
                                                 'PDFs from Google to local folder.')
    parser.add_argument('-c', '--conference', dest='conference',
                        required=True, metavar='CONFERENCE_NAME',
                        help='name of the conference (create scraper tailored to conference type).')
    parser.add_argument('-u', '--url', dest='conference_program_url',
                        required=True, metavar='CONFERENCE_URL',
                        help='URL of the conference program.')
    parser.add_argument('-d', '--destination-dir', dest='destination_dir',
                        required=True, metavar='DIR',
                        help='path to folder where the files will be stored.')
    parser.add_argument('-l', '--log-file', metavar='FILE',
                        help='specify the path to the log file.')
    return parser.parse_args()


if __name__ == '__main__':
    options = parse_options()
    main(options)
