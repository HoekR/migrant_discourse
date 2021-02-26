from typing import Dict, List, Tuple
import requests

from itertools import combinations
from collections import defaultdict
import networkx as nx
from networkx import Graph


COLOR_MAP = {
    'organisation': 'black',
    'academic': 'blue',
    'technocrat': 'red',
    'unknown': 'yellow'
}


def generate_graph():
    return nx.Graph()


def add_entities(graph: Graph, entities: List[Dict[str, any]]):
    nodes = [(entity['entity_name'], {'color': COLOR_MAP[entity['entity_type']]}) for entity in entities]
    graph.add_nodes_from(nodes)


def add_record_links(graph: Graph, record_entities: List[Dict[str, any]]):
    node_labels = [entity['entity_name'] for entity in record_entities]
    for node1, node2 in combinations(node_labels, 2):
        print('adding link', node1, node2)
        graph.add_edge(node1, node2)


def download_spreadsheet_data(spreadsheet_url: str) -> str:
    response = requests.get(spreadsheet_url)
    if response.status_code == 200:
        return response.text
    else:
        raise ValueError(response.text)


def row_has_content(row: List[str]) -> bool:
    for cell in row:
        if cell != '':
            return True
    return False


def parse_spreadsheet_records(spreadsheet_string: str) -> List[Dict[str, any]]:
    rows = [row_string.split('\t') for row_string in spreadsheet_string.split('\r\n')]
    headers = rows[0]
    data_rows = [row for row in rows[1:] if row_has_content(row)]
    records = [{header: row[hi] for hi, header in enumerate(headers)} for row in data_rows]
    for record in records:
        for field in record:
            if field == 'year':
                record[field] = int(record[field])
    return records


def get_spreadsheet_urls() -> Tuple[str, str]:
    spreadsheet_key = '1u691b_EcRfwZ-ipQobFvZZeBJlA0fATErfuymQx_rM8'
    rel_gid = '1337791397'
    ent_gid = '1301599057'
    ent_gid = '1771542502'
    base_url = 'https://docs.google.com/spreadsheets/d/'
    spreadsheet_url_relationships = f'{base_url}{spreadsheet_key}/export?gid={rel_gid}&format=tsv'
    spreadsheet_url_entities = f'{base_url}{spreadsheet_key}/export?gid={ent_gid}&format=tsv'
    return spreadsheet_url_entities, spreadsheet_url_relationships


def retrieve_spreadsheet_records(record_type: str = 'relationships'):
    spreadsheet_url_entities, spreadsheet_url_relationships = get_spreadsheet_urls()
    if record_type == 'entities':
        spreadsheet_string = download_spreadsheet_data(spreadsheet_url_entities)
    elif record_type == 'relationships':
        spreadsheet_string = download_spreadsheet_data(spreadsheet_url_relationships)
    else:
        raise ValueError('Unknown record type, must be "entities" or "relationships"')
    return parse_spreadsheet_records(spreadsheet_string)


def extract_record_entities(record):
    name_map = defaultdict(list)
    publication = {'entity_type': 'publication'}
    record_entities = []
    for header in record:
        if header in ['volume_title', 'series', 'volume', 'year']:
            publication[header] = record[header]
            if header == 'year':
                publication[header] = int(record[header])
        elif header in ['executor_org', 'client', 'funder'] and record[header]:
            entity = {
                'entity_name': record[header],
                'entity_role': header,
                'entity_type': 'organisation'
            }
            record_entities.append(entity)
        elif '_' in header and record[header]:
            field = '_'.join(header.split('_')[:-1])
            name_map[field].append(record[header])
    for field in name_map:
        entity = {
            'entity_name': ', '.join(name_map[field]),
            'entity_role': field[:-1] if field != 'editor' else field,
            'entity_type': 'person'
        }
        if entity['entity_name'] == 'Beijer':
            entity['entity_name'] = 'Beijer, G.'
        record_entities.append(entity)
    record_entities.append(publication)
    return record_entities


def make_bibliographic_record(volume, authors):
    record = {
        'article_title': None,
        'article_doi': None,
        'article_author': None,
        'article_author_index_name': None,
        'article_author_affiliation': None,
        'article_page_range': None,
        'article_pub_date': str(volume['year']),
        'article_pub_year': volume['year'],
        'issue_section': None,
        'issue_number': None,
        'issue_title': None,
        'issue_page_range': None,
        'issue_pub_date': str(volume['year']),
        'issue_pub_year': volume['year'],
        'volume': volume['volume'],
        'journal': volume['series'],
        'publisher': 'REMP'
    }
    if authors[0]['entity_role'] == 'article_author':
        record['issue_section'] = 'article'
        record['article_title'] = volume['volume_title']
    elif authors[0]['entity_role'] == 'preface_author':
        record['issue_section'] = 'front_matter'
        record['article_title'] = 'Preface'
    if authors[0]['entity_role'] == 'preface_author':
        record['issue_section'] = 'front_matter'
        record['article_title'] = 'Introduction'
    record['article_author'] = ' && '.join([author['entity_name'] for author in authors])
    record['article_author_index_name'] = ' && '.join([author['entity_name'] for author in authors])
    record['article_author_affiliation'] = ' && '.join(['' for _author in authors])
    return record


def make_bibliographic_records(relationship_records: List[Dict[str, str]]):
    bib_records = []
    for ri, record in enumerate(relationship_records):
        entities = extract_record_entities(record)
        volume = None
        main_article = []
        preface = []
        introduction = []
        for entity in entities:
            if entity['entity_type'] == 'publication':
                volume = entity
            elif entity['entity_role'] == 'article_author':
                main_article.append(entity)
            elif entity['entity_role'] == 'intro_author':
                introduction.append(entity)
            elif entity['entity_role'] == 'preface_author':
                preface.append(entity)
        bib_record = make_bibliographic_record(volume, main_article)
        bib_records.append(bib_record)
        if len(introduction) > 0:
            bib_record = make_bibliographic_record(volume, introduction)
            bib_records.append(bib_record)
        if len(preface) > 0:
            bib_record = make_bibliographic_record(volume, preface)
            bib_records.append(bib_record)
    return bib_records
