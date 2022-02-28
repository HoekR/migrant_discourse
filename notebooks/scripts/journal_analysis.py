import re
import pandas as pd
import altair as alt
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer

from scripts.data_wrangling import parse_surname, parse_surname_initial, map_dataset
import scripts.content_analysis as ca
from scripts.countries import CountryLookup


def has_topic(title, topic_words):
    for topic_word in topic_words:
        if re.search(r'\b' + topic_word, title.lower()):
            # if topic_word in title.lower():
            return 1
    return 0


def select_df_by_topic(df, topic_words, topic):
    return df[df.article_title.apply(lambda x: has_topic(x, topic_words[topic])) == 1]


def slide_decade(df, window_size: int = 10):
    num_pubs = []
    periods = []
    for start_year in range(1950, 1990):
        end_year = start_year + window_size
        periods.append(f"{start_year}-{end_year}")
        num_pubs.append(len(df[(df.issue_pub_year >= start_year) & (df.issue_pub_year < end_year)]))
    return num_pubs


def get_topics_df(df, topic_words, window_size: int = 5):
    data = {}
    for topic in topic_words:
        topic_df = select_df_by_topic(df, topic_words, topic)
        data[topic] = slide_decade(topic_df, window_size)

    periods = []
    for start_year in range(1950, 1990):
        end_year = start_year + window_size
        periods.append(f"{start_year}-{end_year}")

    data['total'] = slide_decade(df)

    topics_df = pd.DataFrame(data, index=periods)

    for topic in topics_df.columns:
        topics_df[topic] = topics_df[topic] / topics_df['total']

    return topics_df

def extract_country(x):
    c = lookup.extract_countries_continents(x)[0]
    if len(c)>0:
        return(c[0])

def extract_continent(x):
    c = lookup.extract_countries_continents(x)[1]
    if len(c)>0:
        return(c[0])

def make_topics(topic_lists):
    topic_lists = [topic_list[2:] for topic_list in topic_lists.split('\n') if topic_list != '']
    topic_words = {tl.split(': ')[0]: tl.split(': ')[1].split(', ') for tl in topic_lists}
    return topic_words

# the name and location of the article records for the IM journal (in CSV format)
records_file = '../data/main-review-article-records.csv'

columns = ['article_author',
           'article_author_index_name',
           'article_title',
           'issue_pub_year',
           'publisher',
           'article_type']

df = pd.read_csv(records_file, usecols=columns)
df.article_author_index_name.fillna('', inplace=True)
df['article_author_index_name'] = df['article_author_index_name'].str.title()
df['author_surname_initial'] = df.article_author_index_name.apply(parse_surname_initial)
df['issue_pub_decade'] = df.issue_pub_year.apply(lambda x: int(x/10)*10)
df['dataset'] = df.apply(lambda x: map_dataset(x['publisher'], x['article_type']), axis=1)
df['issue_decade'] = df.issue_pub_year.apply(lambda x: int(x/10) * 10 if not pd.isnull(x) else x)
df['normalised_title'] = df.article_title.apply(ca.normalise_title)

bigram_freq = ca.get_bigram_freq(list(df.normalised_title), remove_stop=True)

endings = ['migration', 'immigration', 'emigration']
ending_bigrams = defaultdict(list)
ending_freq = defaultdict(Counter)
lookup = CountryLookup()

for bigram, freq in bigram_freq.most_common(10000):
    for ending in endings:
        if bigram.endswith(f' {ending}'):
            ending_bigrams[ending].append((bigram, freq))


for ending in endings:
    for bigram, freq in ending_bigrams[ending]:
        countries, continents = lookup.extract_countries_continents(bigram, include_nationalities=True)
        #print(bigram, freq, countries, continents)
        ending_freq[ending].update(countries + continents)

df_ending = pd.DataFrame(ending_freq)
df_ending.sort_index(inplace=True)
df_ending.fillna(0)

topic_lists = """
- cause_effect: cause, causal, determinant, factor, influen, setting, effect, affect, impact, consequence, implication
- process: process, dynamic, rate, development, pattern, change, changing, interact, relation, evolution, transform, interpretation, participat
- decision making: policy, policies, politic, decision, management, managing, govern, promotion, planned, recruitment, law, act, implement, amend, guidelines, reform, program, enforcement, legislation, legislative, control, refine, revis, border, international, national, protection, coordination, rationale, administrat, examinat
- labour: labour, labor, worker, work, employment, occupation,
- skill: low-skill, skilled, skill, high-level, professional, intellectual, scientist, brain drain, vocational, vocational training
- legal: illegal, legal, undocumented, unwanted, undesirable, citizenship, right
- forced: involuntary, forced, refuge, refugee, necessity, war, conflict, asylum
- immigration: immigrant, immigrate, immigration
- emigration: emigrant, emigrate, emigration, overseas destination, voluntary return
- migration: migratory, migrant, migración, migrantes, migratoria, migraciones, migraci, arbeitsmigranten, migratori, migrazioni, migratoire, migrações
- group: family, household, community, group
- identity: identity, nationality, nationalism, xenophob, ethnic, race, ideolog, naturali, assimilation, integration, adaptation , absorption
"""

extra = """
- outcome: failure, disenchantment, success, advantage, disadvantage, positive, negative
- business: business, entrep, production, market, industr
- education: education, school, learn
- health: health, medic, disease, epidem
- gender: male, female, gender, women
"""


discipline_lists = """
- psychology: psycholog
- economics: economic, trade
- statistics: statist
- sociology: sociology, social, socio-economic, anthropology, culture
- demography: demography, demographic
"""

discipline_words = make_topics(discipline_lists)
topic_words = make_topics(topic_lists)
for k in topic_words.keys():
    df[k] = df.article_title.apply(lambda x: has_topic(x, topic_words[k]))

# for k in topic_words.keys():
#     print(k, len(df.loc[(df[k]==1)]))
#
# for mt in ['emigration','immigration', 'migration']:
#     lmt = len(df.loc[(df[mt]==1)])
#     for k in topic_words.keys():
#         if k != mt:
#             print(mt, k, round(len(df.loc[(df[mt]==1) & (df[k]==1)])/lmt * 100,2))
#     print('-------')


df['country']=df.normalised_title.apply(extract_country)
df['continent']=df.normalised_title.apply(extract_continent)

stopwords = ca.get_stopwords()
docs = list(df.article_title)
cv=CountVectorizer(stop_words=stopwords, analyzer='word')
word_count_vector=cv.fit_transform(docs)
tfidf_transformer=TfidfTransformer(smooth_idf=True,use_idf=True)
tfidf_transformer.fit(word_count_vector)
df_idf = pd.DataFrame(tfidf_transformer.idf_, index=cv.get_feature_names(),columns=["idf_weights"])
df_idf.sort_values(by=['idf_weights'])

df_remp_im = df[df.dataset == 'REMP_IM']
topics_df = get_topics_df(df_remp_im, discipline_words)

df_imr_research = df[df.dataset == 'IMR_research']
topics_df_imr = get_topics_df(df_imr_research, topic_words)

classified_terms = {}
classified_terms['migration'] = {
    'migration':['migratory', 'migrant', 'migrations','migrants', 'migración', 'migrantes',
                 'migratoria', 'migraciones','migracion', 'migraciín','migrante', 'migracidn','migrationsverhalten',
                 'arbeitsmigranten', 'migratori', 'migrazioni','migratoire', 'migrações', ],
    'integration':['assimilation','integration','adaptation','absorption', 'naturalization','legalization',],
    'emigration':['emigrants', 'emigrant', 'emigracion', 'emigración','emigrazione', 'emigrati','emigração',
                  'emigratión',  'emigranti', 'lémigration', 'émigration','emigrate',],
    'immigration':['immigrants','immigrant','inmigrant', 'immigración', 'immigrazione', 'immigrantes',
                   'inmigrantes', 'inmigration', 'iimmigrants','inmigracion','inmigración','inmigrante', 'immigrate',
                   'immigrati',],
    'remigration':['remigration', 'transmigration', 'transmigrant','reemigracja','euromigration','postmigration','repatriation']}
classified_terms['disciplines'] = {
    'sociology':['sociology', 'sociological', 'sociologique', 'sociologica',  'sociologia', 'sociolinguistics'],
    'statistics':['statistics','statistical'],
    'methods':['methodological','methodologique', 'metodologica','typology','topics','characteristics'],
    'psychology':['psychological','psychology'],
    'politics':['politics','political'],
    'anthropology':['ethnological', 'anthropology','anthropological',],
    'other':['ecology','ecological','ideology','ideological','mythology','demythologizing',
             'technology', 'epidemiology', 'tecnologia', 'technological','biological','cosmology', 'chronology', 'ideologies',
             'economics','ethnics','electronics','ethics']}


temp_df = df[df.normalised_title.str.contains('latin')][['dataset', 'issue_decade']]
s = temp_df.groupby(['dataset', 'issue_decade']).size()
s_unstack = s.unstack('dataset')

g = df.loc[df.author_surname_initial!=''].groupby(['author_surname_initial', 'dataset']).dataset.count()
df_overlap = g.unstack('dataset').fillna(0.0)
#print('number of authors with at least one article in both journals:',
# len(df_overlap[(df_overlap.REMP_IM > 0) & (df_overlap.IMR_research > 0)]))

overlappers = df_overlap[(df_overlap.REMP_IM > 0) & (df_overlap.IMR_research > 0)]
# overlappers
#
# df_overlap[(df_overlap.REMP_IM > 5)]
remp_count=df.loc[(df.author_surname_initial!='')&(df.dataset=="REMP_IM") ]
remp_authors = remp_count.groupby(['author_surname_initial']).agg('count')
remp_freq_authors = remp_authors.loc[remp_authors.article_title>5]['article_title']

fa = list(remp_freq_authors.index)
fra_articles_remp = remp_count.loc[df.author_surname_initial.isin(fa)]
r_topics_df = get_topics_df(fra_articles_remp, discipline_words)

# we declare two different data sets for comparison:
# - df_far is the dataset with frequently publishing authors
# - remp_topics_df is the dataset of the whole of remp_im

df_far = fra_articles_remp
general_topics = {'general': ['cause_effect', 'process', 'decision making', 'labour', 'skill',
                              'legal', 'forced', 'immigration', 'emigration', 'migration', 'group',
                              'identity']}
topics_far_df = get_topics_df(df_far, general_topics)
df_remp_im = df[df.dataset == 'REMP_IM']
remp_topics_df = get_topics_df(df_remp_im, general_topics)

# disp_df = sns.heatmap(aut_tit[['cause_effect', 'process', 'decision making', 'labour', 'skill',
#        'legal', 'forced', 'immigration', 'emigration', 'migration', 'group',
#        'identity']], annot=True)


# def freq_author_graph():
#     out = HTML()
#     collst = ['cause_effect', 'process', 'decision making', 'labour', 'skill',
#            'legal', 'forced', 'immigration', 'emigration', 'migration', 'group',
#            'identity']
#     for aut in fa:
#         aut_tit = df_remp_im.loc[df_remp_im.author_surname_initial==aut]
#
#         h_t = aut_tit[collst]
#         #out = HTML(f)
#         display(HTML(f"<h1>{aut}</h1><br>"))
#         hts = sns.heatmap(h_t[['cause_effect', 'process', 'decision making', 'labour', 'skill',
#            'legal', 'forced', 'immigration', 'emigration', 'migration', 'group',
#            'identity']], annot=True)
#         plt.show()


#
# from IPython.core.display import display, HTML
# out = HTML()
#
# collst = ['issue_decade','cause_effect', 'process', 'decision making', 'labour', 'skill',
#        'legal', 'forced', 'immigration', 'emigration', 'migration', 'group',
#        'identity']
# for aut in fa:
#     aut_tit = df_remp_im.loc[df_remp_im.author_surname_initial==aut]
#     h_t = aut_tit[collst].style.background_gradient(cmap='Blues', subset=collst)
#     #out = HTML(f)
#     display(HTML(f"<h1>{aut}</h1><br>"))
#     display(h_t)
#

# for key in discipline_words:
# for tword in classified_terms[key]:
topic_words.update(discipline_words)
def alt_topic_chart(topicwords=[], topicdf=None, var_name='topics', value_name='number', id_vars='index', title='', scheme='set1', dash=False):
    tpcwrds = topicwords
    selected_topic_words = {topic:topic_words[topic] for topic in tpcwrds}
    plot_df = get_topics_df(topicdf, selected_topic_words).drop('total', axis=1)
    molten = plot_df.reset_index().melt(value_vars=tpcwrds,
                                        var_name=var_name, value_name='number', id_vars='index') #.plot(figsize=(15,5), title="IM use of migration terms", xlabel="years", ylabel="proportion").legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
    molten.rename(columns={"index":'years'}, inplace=True)
    chart1 = alt.Chart(molten).mark_line().encode(
        alt.X('years', type='nominal', axis=alt.Axis(tickCount=10)),
        alt.Y('number', type='quantitative'),
        color=alt.Color(f'{var_name}:O', scale=alt.Scale(scheme=f'{scheme}', reverse=True), title=f'{title}'),
        #strokeDash=f'{var_name}:O'
    )
    chart1.properties(
        title=f'{title}'
    ).configure_title(
        fontSize=20,
        font='Courier',
        align='center',
        color='gray',
    )
    return chart1