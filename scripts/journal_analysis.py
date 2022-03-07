import re
import pandas as pd
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer

import scripts.content_analysis as ca
from scripts.countries import CountryLookup


# for k in topic_words.keys():
#     print(k, len(df.loc[(df[k]==1)]))
#
# for mt in ['emigration','immigration', 'migration']:
#     lmt = len(df.loc[(df[mt]==1)])
#     for k in topic_words.keys():
#         if k != mt:
#             print(mt, k, round(len(df.loc[(df[mt]==1) & (df[k]==1)])/lmt * 100,2))
#     print('-------')


def extra_topics():
    return {'migration': {
        'migration': ['migratory', 'migrant', 'migrations', 'migrants', 'migración', 'migrantes',
                      'migratoria', 'migraciones', 'migracion', 'migraciín', 'migrante', 'migracidn',
                      'migrationsverhalten',
                      'arbeitsmigranten', 'migratori', 'migrazioni', 'migratoire', 'migrações', ],
        'integration': ['assimilation', 'integration', 'adaptation', 'absorption', 'naturalization', 'legalization', ],
        'emigration': ['emigrants', 'emigrant', 'emigracion', 'emigración', 'emigrazione', 'emigrati', 'emigração',
                       'emigratión', 'emigranti', 'lémigration', 'émigration', 'emigrate', ],
        'immigration': ['immigrants', 'immigrant', 'inmigrant', 'immigración', 'immigrazione', 'immigrantes',
                        'inmigrantes', 'inmigration', 'iimmigrants', 'inmigracion', 'inmigración', 'inmigrante',
                        'immigrate',
                        'immigrati', ],
        'remigration': ['remigration', 'transmigration', 'transmigrant', 'reemigracja', 'euromigration',
                        'postmigration', 'repatriation']}, 'disciplines': {
        'sociology': ['sociology', 'sociological', 'sociologique', 'sociologica', 'sociologia', 'sociolinguistics'],
        'statistics': ['statistics', 'statistical'],
        'methods': ['methodological', 'methodologique', 'metodologica', 'typology', 'topics', 'characteristics'],
        'psychology': ['psychological', 'psychology'],
        'politics': ['politics', 'political'],
        'anthropology': ['ethnological', 'anthropology', 'anthropological', ],
        'other': ['ecology', 'ecological', 'ideology', 'ideological', 'mythology', 'demythologizing',
                  'technology', 'epidemiology', 'tecnologia', 'technological', 'biological', 'cosmology', 'chronology',
                  'ideologies',
                  'economics', 'ethnics', 'electronics', 'ethics']}}


def do_rest(df):
    topic_words = get_topic_words()
    discipline_words = get_discipline_words()

    stopwords = ca.get_stopwords()
    docs = list(df.article_title)
    cv = CountVectorizer(stop_words=stopwords, analyzer='word')
    word_count_vector = cv.fit_transform(docs)
    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(word_count_vector)
    df_idf = pd.DataFrame(tfidf_transformer.idf_, index=cv.get_feature_names(), columns=["idf_weights"])
    df_idf.sort_values(by=['idf_weights'])

    # print('number of authors with at least one article in both journals:',
    # len(df_overlap[(df_overlap.REMP_IM > 0) & (df_overlap.IMR_research > 0)]))

    remp_count = df.loc[(df.author_surname_initial != '') & (df.dataset == "REMP_IM")]
    remp_authors = remp_count.groupby(['author_surname_initial']).agg('count')
    remp_freq_authors = remp_authors.loc[remp_authors.article_title > 5]['article_title']

    fa = list(remp_freq_authors.index)

    # we declare two different data sets for comparison:
    # - df_far is the dataset with frequently publishing authors
    # - remp_topics_df is the dataset of the whole of remp_im

    # for key in discipline_words:
    # for tword in classified_terms[key]:
    topic_words.update(discipline_words)


def junkyard():
     disp_df = sns.heatmap(aut_tit[['cause_effect', 'process', 'decision making', 'labour', 'skill',
            'legal', 'forced', 'immigration', 'emigration', 'migration', 'group',
            'identity']], annot=True)

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

