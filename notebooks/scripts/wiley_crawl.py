from typing import Dict, List, Tuple, Union
import os
import random
import time
import requests
from requests import Session
import re

from bs4 import BeautifulSoup


def retrieve_year_volume_soup(year: int, session: Session) -> BeautifulSoup:
    print(f'getting volume issue list for year {year}')
    url = f'https://onlinelibrary.wiley.com/loi/14682435/year/{year}'
    return retrieve_url_soup(url, session)


def retrieve_url_soup(url: str, session: Session) -> BeautifulSoup:
    response = session.get(url, headers=get_headers())
    return BeautifulSoup(response.content, 'lxml')


def retrieve_year_issue_urls(year: int, session: Session) -> List[str]:
    volume_soup = retrieve_year_volume_soup(year, session)
    volume_main_soup = volume_soup.find('div', class_='main-content')
    volume_list_soup = volume_main_soup.find(class_='loi__issues')
    return [extract_issue_url(volume_issue_soup) for volume_issue_soup in volume_list_soup.find_all('li')]


def extract_issue_url(volume_issue_soup: BeautifulSoup) -> str:
    base_url = 'https://onlinelibrary.wiley.com'
    relative_url = volume_issue_soup.find('a')['href']
    absolute_url = base_url + relative_url
    return absolute_url


def download_issue(year: int, issue_url: str, session: Session, data_dir: str) -> None:
    issue_soup = retrieve_url_soup(issue_url, session)
    write_issue_html(year, issue_url, issue_soup, data_dir)


def write_issue_html(year: int, issue_url: str, issue_soup: BeautifulSoup, data_dir: str) -> None:
    issue = issue_url.split('/')[-1].replace('%E2%80%90', '-')
    print(f'writing issue html for year {year}, issue {issue}')
    output_filename = f'Internationl_Migration-{year}-{issue}.html'
    output_filepath = os.path.join(data_dir, output_filename)
    with open(output_filepath, 'wt') as fh:
        fh.write(issue_soup.prettify())


def get_headers() -> Dict[str, str]:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.142 Safari/537.36'
    return {
        'User-agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-gb',
    }


def do_crawl():
    data_dir = '../../data/wiley-crawl/'
    session = requests.Session()
    min_wait = 15
    random_wait = 15
    for year in range(1961, 2012):
        issue_urls = retrieve_year_issue_urls(year, session)
        wait_time = min_wait + random.random() * random_wait
        print('waiting', wait_time)
        time.sleep(wait_time)
        for issue_url in issue_urls:
            download_issue(year, issue_url, session, data_dir)
            wait_time = min_wait + random.random() * random_wait
            print('waiting', wait_time)
            time.sleep(wait_time)


def parse_text(text: str) -> str:
    return text.replace('\u2010', '-').replace('\u2019', "'")


def read_file_soup(fname: str) -> BeautifulSoup:
    with open(fname, 'rt') as fh:
        content = fh.read()
        return BeautifulSoup(content, 'lxml')


def extract_article_title(issue_item_soup: BeautifulSoup) -> str:
    title_soup = issue_item_soup.find(class_='issue-item__title')
    return re.sub(r'[\n ]{2,}', ' ', parse_text(title_soup.text.strip()))


def extract_article_doi(issue_item_soup: BeautifulSoup) -> str:
    base_url = 'https://onlinelibrary.wiley.com'
    title_soup = issue_item_soup.find(class_='issue-item__title')
    relative_url = title_soup['href']
    absolute_url = base_url + relative_url
    return absolute_url


def extract_article_author(issue_item_soup: BeautifulSoup) -> Union[None, str]:
    author_soup = issue_item_soup.find('ul', class_='loa-authors-trunc')
    authors = []
    if author_soup is None:
        return None
    for li in author_soup.find_all('li'):
        authors.append(parse_text(li.text.strip()))
    return ' & '.join(authors)


def extract_article_details(issue_item_soup: BeautifulSoup) -> Tuple[str, str]:
    detail_soup = issue_item_soup.find(class_='issue-item__details')
    page_range, pub_date = None, None
    for li in detail_soup.find_all('li'):
        if 'page-range' in li.attrs['class']:
            page_range = parse_text(li.text.strip())
            page_range = re.sub(r'[\n ]+', '', page_range.replace('Pages:', ''))
        if 'ePubDate' in li.attrs['class']:
            pub_date = parse_text(li.text.strip())
            pub_date = re.sub(r'[\n ]{2,}', '', pub_date.replace('First Published:', ''))
    return page_range, pub_date


def extract_issue_item_record(issue_item_soup: BeautifulSoup) -> Dict[str, Union[None, str]]:
    record = {
        'article_title': extract_article_title(issue_item_soup),
        'article_doi': extract_article_doi(issue_item_soup),
        'article_author': extract_article_author(issue_item_soup)
    }
    page_range, pub_date = extract_article_details(issue_item_soup)
    record['article_page_range'] = page_range
    record['article_pub_date'] = pub_date
    match = re.search(r'\d{4}', pub_date)
    record['article_pub_year'] = int(match.group(0)) if match else None
    return record


def extract_issue_details(issue_soup: BeautifulSoup) -> Dict[str, Union[str, int]]:
    year, volume, issue, issue_title = None, None, None, None
    for meta_soup in issue_soup.find_all('meta'):
        if 'property' in meta_soup.attrs and meta_soup.attrs['property'] == 'og:url':
            year, volume, issue = meta_soup.attrs['content'].split('/')[-3:]
            year = int(year)
            volume = int(volume)
            issue = issue.replace('%E2%80%90', '-')
        if 'property' in meta_soup.attrs and meta_soup.attrs['property'] == 'og:title':
            issue_title = meta_soup.attrs['content']
    journal_soup = issue_soup.find('div', class_='journal-info-container')
    journal_title = journal_soup.text.strip()
    details_soup = issue_soup.find('div', class_='cover-image__details')
    page_range_soup = details_soup.find('div', class_='cover-image__pageRange')
    page_range = page_range_soup.find('span').text.strip()
    issue_date_soup = details_soup.find('div', class_='cover-image__date')
    issue_pub_date = issue_date_soup.find('span').text.strip()
    issue_details = {
        'journal': journal_title,
        'volume': volume,
        'issue': issue,
        'issue_title': issue_title,
        'issue_page_range': page_range,
        'issue_pub_date': issue_pub_date,
        'issue_pub_year': year
    }
    return issue_details


def extract_issue_records(issue_soup: BeautifulSoup) -> List[Dict[str, Union[str, int]]]:
    issue_details = extract_issue_details(issue_soup)
    toc_div = issue_soup.find('div', class_='table-of-content')
    records = []
    for issue_item_soup in toc_div.find_all('div', class_='issue-item'):
        record = extract_issue_item_record(issue_item_soup)
        for key in issue_details:
            record[key] = issue_details[key]
        records.append(record)
    return records
