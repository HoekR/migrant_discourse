from typing import Dict, List, Tuple, Union
import os
import random
import time
import requests
from requests import Session
import re
from urllib.parse import unquote


from bs4 import BeautifulSoup


# field that can have multiple values need to be joined into a string
# use JOIN_STRING as the value separator
JOIN_STRING = ' && '


#########################
# generic crawling code #
#########################


def get_headers() -> Dict[str, str]:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.142 Safari/537.36'
    return {
        'User-agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-gb',
    }


def retrieve_url_soup(url: str, session: Session, min_wait: int, random_wait: int) -> BeautifulSoup:
    print('retrieving url', url)
    response = session.get(url, headers=get_headers())
    wait_time = min_wait + random.random() * random_wait
    print('waiting', wait_time)
    time.sleep(wait_time)
    return BeautifulSoup(response.content, 'lxml')


def parse_text(text: str) -> str:
    return text.replace('\u2010', '-').replace('\u2013', '-').replace('\u2018', "'").replace('\u2019', "'")


def read_file_soup(fname: str) -> BeautifulSoup:
    with open(fname, 'rt') as fh:
        content = fh.read()
        return BeautifulSoup(content, 'lxml')


#################
# Wiley parsing #
#################


def retrieve_wiley_year_volume_soup(year: int, session: Session, min_wait: int, random_wait: int) -> BeautifulSoup:
    print(f'getting volume issue list for year {year}')
    url = f'https://onlinelibrary.wiley.com/loi/14682435/year/{year}'
    return retrieve_url_soup(url, session, min_wait, random_wait)


def retrieve_wiley_year_issue_urls(year: int, session: Session, min_wait: int, random_wait: int) -> List[str]:
    volume_soup = retrieve_wiley_year_volume_soup(year, session, min_wait, random_wait)
    volume_main_soup = volume_soup.find('div', class_='main-content')
    volume_list_soup = volume_main_soup.find(class_='loi__issues')
    return [extract_wiley_issue_url(volume_issue_soup) for volume_issue_soup in volume_list_soup.find_all('li')]


def extract_wiley_issue_url(volume_issue_soup: BeautifulSoup) -> str:
    base_url = 'https://onlinelibrary.wiley.com'
    relative_url = volume_issue_soup.find('a')['href']
    absolute_url = base_url + relative_url
    return absolute_url


def download_wiley_issue(year: int, issue_url: str, session: Session, data_dir: str,
                         min_wait: int, random_wait: int) -> None:
    issue_soup = retrieve_url_soup(issue_url, session, min_wait, random_wait)
    write_wiley_issue_html(year, issue_url, issue_soup, data_dir)


def write_wiley_issue_html(year: int, issue_url: str, issue_soup: BeautifulSoup, data_dir: str) -> None:
    issue = issue_url.split('/')[-1].replace('%E2%80%90', '-')
    print(f'writing issue html for year {year}, issue {issue}')
    output_filename = f'Internationl_Migration-{year}-{issue}.html'
    output_filepath = os.path.join(data_dir, output_filename)
    with open(output_filepath, 'wt') as fh:
        fh.write(issue_soup.prettify())


def do_wiley_crawl():
    data_dir = '../../data/wiley-IM-crawl/'
    session = requests.Session()
    min_wait = 15
    random_wait = 15
    for year in range(1961, 2012):
        issue_urls = retrieve_wiley_year_issue_urls(year, session, min_wait, random_wait)
        for issue_url in issue_urls:
            download_wiley_issue(year, issue_url, session, data_dir, min_wait, random_wait)


def extract_wiley_article_title(issue_item_soup: BeautifulSoup) -> str:
    title_soup = issue_item_soup.find(class_='issue-item__title')
    return re.sub(r'[\n ]{2,}', ' ', parse_text(title_soup.text.strip()))


def extract_wiley_article_doi(issue_item_soup: BeautifulSoup) -> str:
    base_url = 'https://onlinelibrary.wiley.com'
    title_soup = issue_item_soup.find(class_='issue-item__title')
    relative_url = title_soup['href']
    absolute_url = base_url + relative_url
    return absolute_url


def extract_wiley_article_author(issue_item_soup: BeautifulSoup) -> Union[None, str]:
    author_soup = issue_item_soup.find('ul', class_='loa-authors-trunc')
    authors = []
    if author_soup is None:
        return None
    for li in author_soup.find_all('li'):
        authors.append(parse_text(li.text.strip()))
    return JOIN_STRING.join(authors)


def extract_wiley_article_author_index_name(issue_item_soup: BeautifulSoup) -> Union[None, str]:
    author_soup = issue_item_soup.find('ul', class_='loa-authors-trunc')
    authors = []
    if author_soup is None:
        return None
    for li in author_soup.find_all('li'):
        author_url = unquote(li.find('a')['href'])
        authors.append(author_url.split('ContribAuthorStored=')[1].replace('+', ' '))
    return JOIN_STRING.join(authors)


def extract_wiley_article_details(issue_item_soup: BeautifulSoup) -> Tuple[str, str]:
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


def extract_wiley_issue_item_record(issue_item_soup: BeautifulSoup) -> Dict[str, Union[None, str]]:
    record = {
        'article_title': extract_wiley_article_title(issue_item_soup),
        'article_doi': extract_wiley_article_doi(issue_item_soup),
        'article_author': extract_wiley_article_author(issue_item_soup),
        'article_author_index_name': extract_wiley_article_author_index_name(issue_item_soup),
        'article_author_affiliation': None
    }
    if record['article_author'] is not None:
        authors = record['article_author'].split(JOIN_STRING)
        record['article_author_affiliation'] = JOIN_STRING.join(['' for _ in authors])
    page_range, pub_date = extract_wiley_article_details(issue_item_soup)
    record['article_page_range'] = page_range
    record['article_pub_date'] = pub_date
    match = re.search(r'\d{4}', pub_date)
    record['article_pub_year'] = int(match.group(0)) if match else None
    return record


def extract_wiley_issue_details(issue_soup: BeautifulSoup) -> Dict[str, Union[str, int]]:
    year, volume, issue, issue_title = None, None, None, None
    for meta_soup in issue_soup.find_all('meta'):
        if 'property' in meta_soup.attrs and meta_soup.attrs['property'] == 'og:url':
            year, volume, issue = meta_soup.attrs['content'].split('/')[-3:]
            year = int(year)
            volume = volume
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
        'issue_number': issue,
        'issue_title': issue_title,
        'issue_page_range': page_range,
        'issue_pub_date': issue_pub_date,
        'issue_pub_year': year,
        'volume': volume,
        'journal': journal_title
    }
    return issue_details


def extract_wiley_issue_records(issue_soup: BeautifulSoup) -> List[Dict[str, Union[str, int]]]:
    issue_details = extract_wiley_issue_details(issue_soup)
    toc_div = issue_soup.find('div', class_='table-of-content')
    records = []
    for section_soup in toc_div.find_all('div', class_='issue-items-container'):
        issue_section = section_soup.find(class_='section__header').text.strip()
        for issue_item_soup in section_soup.find_all('div', class_='issue-item'):
            record = extract_wiley_issue_item_record(issue_item_soup)
            record['issue_section'] = issue_section
            for key in issue_details:
                record[key] = issue_details[key]
            record['publisher'] = 'Wiley'
            records.append(record)
    return records


################
# Sage parsing #
################


def extract_sage_issue_title(issue_soup: BeautifulSoup) -> str:
    title_soup = issue_soup.find('div', class_='journalNavTitle')
    return title_soup.text.strip()


def extract_sage_article_records(issue_soup) -> List[Dict[str, any]]:
    records = []
    issue_details = extract_sage_issue_metadata(issue_soup)
    for article_soup in issue_soup.find_all('table', class_='articleEntry'):
        article_record = extract_sage_article_info(article_soup)
        for key in issue_details:
            article_record[key] = issue_details[key]
        article_record['publisher'] = 'Sage Publishing'
        records.append(article_record)
    return records


def extract_sage_issue_metadata(issue_soup: BeautifulSoup):
    year, volume, issue = None, None, None
    journal_title, issue_title, issue_page_range, issue_pub_date = None, None, None, None
    issue_pub_year = None
    for meta_soup in issue_soup.find_all('meta'):
        if 'property' in meta_soup.attrs and meta_soup.attrs['property'] == 'og:url':
            volume, issue = meta_soup.attrs['content'].split('/')[-2:]
            issue = issue.replace('%E2%80%90', '-')
        if 'property' in meta_soup.attrs and meta_soup.attrs['property'] == 'og:title':
            issue_title = meta_soup.attrs['content']
            journal_title = issue_title.split(' - ')[0]
            match = re.search(r'Number .*?, (.*\d{4})$', issue_title)
            if match:
                issue_pub_date = match.group(1)
            else:
                raise ValueError(f'Unexpected issue pub date format: {issue_title}')
            issue_pub_year = int(issue_pub_date[-4:])
    issue_details = {
        'issue_number': issue,
        'issue_title': issue_title,
        'issue_page_range': issue_page_range,
        'issue_pub_date': issue_pub_date,
        'issue_pub_year': issue_pub_year,
        'volume': volume,
        'journal': journal_title
    }
    return issue_details


def extract_sage_article_info(article_soup: BeautifulSoup) -> Dict[str, any]:
    authors = extract_sage_article_authors(article_soup)
    # print(authors)
    article_info = {
        'article_title': article_soup.find('span', class_='hlFld-Title').text.strip(),
        'article_doi': extract_sage_article_doi(article_soup),
        'article_author': JOIN_STRING.join([author['author_name'] for author in authors]),
        'article_author_index_name': JOIN_STRING.join([author['author_index_name'] for author in authors]),
        'article_author_affiliation': JOIN_STRING.join([author['author_affiliation'] for author in authors]),
        'article_page_range': extract_sage_article_page_range(article_soup),
        'article_pub_date': extract_sage_article_pub_date(article_soup),
        'article_pub_year': int(extract_sage_article_pub_date(article_soup)[-4:]),
        'issue_section': article_soup.find('span', class_='ArticleType').text.strip()
    }
    return article_info


def extract_sage_article_doi(article_soup: BeautifulSoup):
    doi_link = article_soup.find('div', class_='art_title').find('a')['href']
    return 'https://journals.sagepub.com' + doi_link


def extract_sage_article_authors(article_soup: BeautifulSoup) -> List[Dict[str, str]]:
    authors: List[Dict[str, str]] = []
    for author_soup in article_soup.find_all('span', class_='contribDegrees'):
        strings = [string for string in author_soup.find('div', class_='author-section-div').stripped_strings]
        author_url = unquote(author_soup.find('a')['href'])
        author = {
            'author_name': author_soup.find('a').text.strip(),
            'author_affiliation': strings[0] if strings[0] != 'See all articles' else '',
            'author_index_name': author_url.split('ContribAuthorStored=')[1].replace('+', ' ')
        }
        authors.append(author)
    return authors


def extract_sage_article_pub_date(article_soup: BeautifulSoup):
    strings = [string for string in article_soup.find('span', class_='tocEPubDate').stripped_strings]
    article_pub_date = strings[-1].strip()
    return article_pub_date


def extract_sage_article_page_range(article_soup: BeautifulSoup):
    article_page_range = article_soup.find('span', class_='articlePageRange').text.strip()
    if '; pp. ' not in article_page_range:
        raise ValueError(f'Unknown page range format: {article_page_range}')
    article_page_range = parse_text(article_page_range.replace('; pp. ', ''))
    return article_page_range


def write_sage_issue_html(issue_soup, journal_dir, issue_info):
    journal = issue_info['journal_title'].replace(' ', '_')
    volume = issue_info['volume']
    issue = issue_info['issue']
    issue_filename = f"{journal}-{volume}-{issue}.html"
    issue_filepath = os.path.join(journal_dir, issue_filename)
    with open(issue_filepath, 'wt') as fh:
        fh.write(issue_soup.prettify())


def extract_sage_issue_links(main_soup):
    for issue_div_soup in main_soup.find_all('div', class_='js_issue'):
        for issue_link_soup in issue_div_soup.find_all('a', class_='issue-link'):
            issue_url = issue_link_soup['href']
            journal_acronym, volume, issue = issue_url.split('/')[-3:]
            yield {
                'journal_title': 'International Migration Review',
                'journal_acronym': journal_acronym,
                'volume': volume,
                'issue': issue,
                'issue_url': issue_url
            }
    return None


def do_sage_crawl(journal_dir: str, issue_overview_file: str):
    main_soup = read_file_soup(issue_overview_file)
    session = requests.Session()
    min_wait = 15
    random_wait = 15
    for issue_info in extract_sage_issue_links(main_soup):
        issue_soup = retrieve_url_soup(issue_info['issue_url'], session, min_wait, random_wait)
        write_sage_issue_html(issue_soup, journal_dir, issue_info)
    return None
