#!/usr/bin/env python
# coding: utf-8

import sys

from network_overlap import pub_df, vals
from .network_visualisation import surnms, record_entities, entity_count, entity_role_count, entities, nodelist

sys.path.append('/data/home/jupyter-jdh-artikel/.local/lib/python3.7/site-packages')

import pandas as pd
# import altair as alt

from itertools import chain
from collections import defaultdict, Counter
# import networkx as nx

from scripts.network_analysis import retrieve_spreadsheet_records
from scripts.network_analysis import extract_record_entities

from scripts.network_analysis import generate_graph, add_entities, add_record_links
from scripts.data_wrangling import *

entity_records = retrieve_spreadsheet_records(record_type='entities')
entity_records = lowercase_headers(entity_records)
entity_roles = {get_entity_name(record): [record['prs_role1'], record['prs_role2'], record['prs_role3']] for record in entity_records}

for k in entity_roles:
    nr = [e for e in entity_roles[k] if e !='']
    entity_roles[k]=nr

entity_category = {get_entity_name(entity = record): record.get('prs_category') or 'unknown' for record in entity_records}

relationship_records = retrieve_spreadsheet_records(record_type='relationships')
er = list(set(chain.from_iterable(entity_roles.values())))

categorized_persons = retrieve_spreadsheet_records("categories")
categorized_persons = lowercase_headers(categorized_persons)

# we convert these into a dataframe for easier selection
cat_p_df = pd.DataFrame(categorized_persons)
cat_p_df['fullname'] = cat_p_df.apply(lambda row: get_entity_name(entity=row), axis=1)



namecolumns = ['{author}_surname','{author}_infix', '{author}_initials']
t_authors = ['article_author1',
             'article_author2',
             'preface_author1',
             'preface_author2',
             'intro_author1',
             'intro_author2',
             'editor']

relrecs = pd.DataFrame(relationship_records)
for c in ['year']:
    relrecs[c] = relrecs[c].astype('int')

for a in t_authors:
    clst = [c.format(author=a) for c in namecolumns]
    colnm = '{a}'.format(a=a)
    relrecs[colnm] = relrecs[clst].apply(lambda x: aut_to_fn(x), axis=1)


keepcolumns = ['series', 'volume', 'volume_title', 'year', 'funder', 'client', 'executor_org'] + t_authors
cleanrecs = relrecs[keepcolumns].fillna('')
period_results = defaultdict(dict)
for period in periods:
    recs = cleanrecs.loc[relrecs.year.isin(range(periods[period]['start'],periods[period]['end']))]
    recnrs = len(recs)
    period_results[period]['nr of titles'] = recnrs
    relationfields = t_authors + ['executor_org','funder', 'client']
    for c in relationfields:
        period_results[period][c] = len(recs[c].unique())

nodes = {'authors':['article_author1','article_author2'],
'pref_a' : ['preface_author1', 'preface_author2',],
'intro_a' : ['intro_author1', 'intro_author2'],
'editor' : ['editor'],
'funder' : ['funder'],
'executor_org':['executor_org']}

overall_results = {}
for c in t_authors + ['funder', 'client', 'executor_org']:
    overall_results[c] = list(relrecs[c].unique())

cnted = {}
for key in nodes:
    allaut = Counter()
    cnted[key] = Counter()
    for f in nodes[key]:
        cnted[key].update(cleanrecs[f].value_counts().to_dict())
overview = pd.DataFrame(cnted).fillna(0)
overview.drop(index='', inplace=True)
overview['total'] = overview.agg('sum', axis=1)

for column in overview.columns:
    overview[column] = overview[column].astype('int')

freq_auts = overview.loc[overview.authors > 1]
auts = overview.loc[overview.authors > 0]

aut_category = {}
for aut in auts.index:
    n = ', '.join(aut.split(',  '))
    aut_category[n] = entity_category.get(n) or 'unknown'

autlst = list([', '.join(aut.split(',  ')) for aut in auts.index])
cat_p_df.loc[cat_p_df.fullname.isin(autlst)][['fullname','prs_country']].prs_country.value_counts()
aut_category = {}
for aut in auts.index:
    n = ', '.join(aut.split(',  '))
    aut_category[n] = entity_category.get(n) or 'unknown'
autcat = pd.DataFrame().from_dict(aut_category, orient="index")
aut_country = {}

entity_nationality = {get_entity_name(entity = record): record.get('prs_country') or 'unknown' for record in entity_records}


entities = [', '.join(n.split(',  ')) for n in list(overview.index)]
entity_nationality2 = cat_p_df.loc[cat_p_df.fullname.isin(entities)][['fullname', 'prs_country']]
entity_nationality_sn = cat_p_df.loc[cat_p_df.prs_surname.isin(surnms)]

 # = cat_p_df.loc[cat_p_df.fullname.isin(list(overview.index))]


for aut in auts.index:
    n = ', '.join(aut.split(',  '))
    aut_country[n] = entity_nationality.get(n) or 'unknown'
autcountry = pd.DataFrame().from_dict(aut_country, orient="index")
sups = overview.loc[(overview.funder>0)|(overview.pref_a>0)].sort_values(by='total', ascending=False)
sup_country = {}
for sup in sups.index:
    n = ', '.join(aut.split(',  '))
    sup_country[n] = entity_nationality.get(n) or 'unknown'
supcountry = pd.DataFrame().from_dict(sup_country, orient='index')
supcountry.loc[supcountry[0]!='unknown'].value_counts()
overview.loc[(overview.authors >0) & (overview.total > overview.authors)]
subgraphs = {}
