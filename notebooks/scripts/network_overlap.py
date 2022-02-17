import pandas as pd
import numpy as np
from itertools import chain
from scripts.datasets import category_records
from scripts.data_wrangling import *

def chainer(s):
    return list(chain.from_iterable(s.fillna('').str.split(' && ')))


def cutdecade(x, decade):
    result = False
    if x.right < decade[0]:
        return False
    if x.left > decade[1]:
        return False
    if x.left > decade[0] or x.right >= decade[0]:
        return True

# load the csv data into a data frame
records_file = '../data/main-review-article-records.csv'
pub_df = pd.read_csv(records_file)

# Code adapted from https://stackoverflow.com/questions/50731229/split-cell-into-multiple-rows-in-pandas-dataframe

pub_df['dataset'] = pub_df.apply(lambda x: map_dataset(x['publisher'], x['article_type']), axis=1)

# calculate lengths of splits
lens = pub_df['article_author'].fillna('').str.split(' && ').map(len)

# create new dataframe, repeating or chaining as appropriate
split_pub_df = pd.DataFrame({
    'journal': np.repeat(pub_df['journal'], lens),
    'issue_pub_year': np.repeat(pub_df['issue_pub_year'], lens),
    'publisher': np.repeat(pub_df['publisher'], lens),
    'dataset': np.repeat(pub_df['dataset'], lens),
    'article_author': chainer(pub_df['article_author']),
    'article_author_index_name': chainer(pub_df['article_author_index_name']),
    'article_author_affiliation': chainer(pub_df['article_author_affiliation'])
})

split_pub_df = split_pub_df.reset_index(drop=True)

# Make sure title case is used consistently in the author index name column
split_pub_df['article_author_index_name'] = split_pub_df['article_author_index_name'].str.title()
# add a column with surname and first name initial extracted from the author index name
split_pub_df['author_surname_initial'] = split_pub_df.article_author_index_name.apply(parse_surname_initial)
# add a column with surname only
split_pub_df['author_surname'] = split_pub_df.article_author_index_name.apply(parse_surname)
# add a column with the decade in which the issue was published that contains an article
split_pub_df['issue_pub_decade'] = split_pub_df.issue_pub_year.apply(lambda x: int(x/10)*10)
# map journal names to their acronyms
split_pub_df.journal = split_pub_df.journal.apply(acronym)

# remove articles with no authors
split_pub_df =  split_pub_df[split_pub_df.article_author != '']


board_df = pd.DataFrame(category_records)
board_df['article_author_index_name'] = board_df.apply(parse_author_index_name, axis=1)
board_df['author_surname_initial'] = board_df.article_author_index_name.apply(parse_surname_initial)
board_df['period'] = board_df.apply(lambda x: yr2cat(x), axis=1)

decades = {1950:(1950, 1960),
 1960:(1960, 1970),
 1970:(1970, 1980),
 1980:(1980, 1990),
 1990:(1990, 2000),
 2000:(2000, 2010)
          }


for key in decades:
    decade = decades[key]
    board_df[key] = board_df.period.apply(lambda x: cutdecade(x, decade))

decade_cols = [1950, 1960, 1970, 1980, 1990]
org_cols = ['author_surname_initial', 'organisation']
display_cols =  org_cols + decade_cols

temp_board_df = board_df[org_cols].merge(board_df[decade_cols].astype(int), left_index=True, right_index=True)
temp_board_df = temp_board_df.rename(columns={'dataset': 'cat'})
temp_board_df['in_board'] = 1

decade_pub_df = pd.get_dummies(split_pub_df.issue_pub_decade)

temp_pub_df = split_pub_df[['author_surname_initial', 'dataset']].merge(decade_pub_df, left_index=True, right_index=True)
temp_pub_df = temp_pub_df.rename(columns={'dataset': 'cat'})
temp_pub_df = temp_pub_df.groupby(['author_surname_initial', 'cat']).sum().reset_index()
temp_pub_df['in_pub'] = 1
# temp_pub_df

# Hernoem temp_df naar iets inhoudelijks
temp_df = pd.concat([temp_board_df.rename(columns={'organisation': 'cat'}).set_index('author_surname_initial'),
                     temp_pub_df.rename(columns={'dataset': 'cat'}).set_index('author_surname_initial')])

for name in temp_df.index:
    temp_df.loc[name,'in_pub'] = temp_df.loc[name,'in_pub'].max()
    temp_df.loc[name,'in_board'] = temp_df.loc[name,'in_board'].max()
temp_df = temp_df.reset_index()

temp2_df = temp_df[(temp_df.in_board == 1) & (temp_df.in_pub == 1)].drop(['in_board', 'in_pub'], axis=1)
temp2_df.sort_values(by='author_surname_initial').style.apply(highlight_decade, axis=1)
#
# temp_df['total'] = temp_df[['1950', '190']].sum(axis=1).groupby('author_surname_initial').agg('sum')

decade_board_df = board_df[org_cols+['prs_country']].merge(board_df[decade_cols].astype(int), left_index=True, right_index=True)
decade_board_df = decade_board_df.rename(columns={'dataset': 'cat'})
decade_board_df['in_board'] = 1

n_all = temp_df.author_surname_initial.unique()
n_authors = temp_df.loc[temp_df.in_pub>0].author_surname_initial.unique()
n_board = temp_df.loc[temp_df.in_board>0].author_surname_initial.unique()
n_board_and_author = temp_df.loc[(temp_df.in_board>0) & (temp_df.in_pub>0)].author_surname_initial.unique()