import re
import unicodedata
import string

import pandas as pd

all_letters = string.ascii_letters + " .,;'-"


# Turn a Unicode string to plain ASCII, thanks to https://stackoverflow.com/a/518232/2809427
def unicode_to_ascii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
        and c in all_letters
    )


def acronym(text_string):
    if text_string == 'International Migration':
        return 'IM'
    else:
        return 'IMR'


def normalise_name(author_name):
    author_name = unicode_to_ascii(author_name)
    author_name = author_name.title()
    author_name = author_name.replace('Abandan-Unat', 'Abadan-Unat')
    author_name = author_name.replace('Bastos De Avila', 'Avila')
    # Jr. is dropped from the index name
    author_name = author_name.replace('Purcell Jr.', 'Purcell')
    # Titles like Father
    titles = ['Father ', 'Ambassador ']
    for title in titles:
        if title in author_name:
            author_name = author_name.replace(title, ' ')
    # Prefix in Spanish and French: Por and Par
    if ' Por ' in author_name:
        author_name = author_name.replace(' Por ', ' ')
    if ' Par ' in author_name:
        author_name = author_name.replace(' Par ', ' ')
    author_name = re.sub(r' +', ' ', author_name)
    return author_name.strip()


def parse_surname(author_name: str):
    author_name = normalise_name(author_name)
    return ','.join(author_name.split(',')[:-1]).replace('ij', 'y').title()


def parse_surname_initial(author_name: str):
    author_name = normalise_name(author_name)
    if ',' not in author_name:
        return author_name
    surname = ','.join(author_name.split(',')[:-1]).replace('ij', 'y').title()
    initial = author_name.split(', ')[-1][0]
    return f'{surname}, {initial}'


def parse_author_index_name(row):
    if row['prs_infix'] != '':
        return ', '.join([row['prs_surname'], row['prs_infix'], row['prs_initials']])
    else:
        return ', '.join([row['prs_surname'], row['prs_initials']])


#########################
# Generic Data Handling #
#########################


def map_dataset(publisher, article_type):
    # all REMP and IM (published by Wiley) articles are bunlded in a single dataset
    if publisher == 'Staatsdrukkerij' or publisher == 'Wiley':
        return 'REMP_IM'
    # The IMR articles are separated in review articles and research articles
    return 'IMR_research' if article_type == 'main' else 'IMR_review'


def yr2cat(x):
    s = x['period_start']
    e = x['last_known_date']
    try:
        start = int(s)
    except ValueError:
        start = 0
    try:
        end = int(e)
    except ValueError:
        end = start
    return pd.Interval(start, end, closed='both')


def map_bool(value):
    if isinstance(value, bool):
        return 1 if value else 0
    else:
        return value


def is_decade(value):
    return isinstance(value, int)


def highlight_decade(row):
    color_cat = {
        'Dutch Government': '#ffbbbb',
        'ICEM': '#ff6666',
        'REMP': '#ff0000',
        'REMP_IM': '#0000ff',
        'IMR_research': '#8888ff',
        'IMR_review': '#bbbbff',
    }
    color = color_cat[row['cat']]
    return [f'background-color: {color}' if is_decade(col) and row[col] else '' for col in row.keys()]

def lowercase_headers(records:list):
    return [dict((k.lower(), v) for k,v in record.items()) for record in records]


def get_entity_category(entity: dict, entity_category: dict):
    if entity.get('entity_name') in entity_category:
        return entity_category[entity['entity_name']]
    else:
        return 'unknown'


def get_entity_name(entity: dict, ):
    name_labels = ['prs_surname', 'prs_infix', 'prs_initials']
    if entity['prs_infix'] != '':
        return f"{entity['prs_surname'].strip()}, {entity['prs_infix'].strip()}, {entity['prs_initials'].strip()}"
    else:
        return f"{entity['prs_surname'].strip()}, {entity['prs_initials'].strip()}"


def get_entity_country(entity: dict):
    if entity.get('entity_name') in entity_category:
        return entity_category[entity['entity_name']]
    else:
        return 'unknown'


def make_nodes(entity):
    return [n.get('entity_name') for n in entity if n.get('entity_name')]


def make_link_from_entity(entity, revnodelist, rempgraph):
    counter = []
    authors = [n.get('entity_name') for n in entity if n.get('entity_role')=='article_author']
    links = []
    for aut in authors:
        autnr = revnodelist[aut]
        counter.append(autnr)
        for node in entity:
            if node.get('entity_role') != 'article_author':
                if node.get('entity_role'): # we don't include titles
                    category = node.get('entity_role') or "unknown"
                    target = revnodelist[node.get('entity_name')]
                    graphnode = rempgraph.nodes()[target]
                    if graphnode.get('category'):
                        graphnode['category'].append(category)
                    else:
                        graphnode['category'] = [category]
                    link = (autnr, target, {"link_type": node.get('entity_role') or 'unknown'})
                    links.append(link)
                    counter.append(target)

    return links, counter


def aut_to_fn(cols):
    if cols[0].strip() != '':
         return f'{cols[0]+","} {cols[1]} {cols[2] or ""}'.strip()