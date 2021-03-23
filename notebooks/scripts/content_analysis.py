from typing import List
from collections import Counter, defaultdict
import re

from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from nltk.corpus import stopwords as stopword_sets
from pandas import DataFrame
import pandas as pd
from nltk import pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()


def map_pos(pos):
    """Map NLTK Part-Of-Speech tag labels to WordNet Part-Of-Speech tag labels."""
    if pos.startswith('NN'):
        return 'n'
    if pos.startswith('VB'):
        return 'v'
    if pos.startswith('A'):
        return 'a'


def lemmatize_words(words):
    """Return the lemmas of a list of words."""
    return [lemmatizer.lemmatize(word, pos=map_pos(pos)) if map_pos(pos) else word for word, pos in pos_tag(words)]


def lemmatize_title(title):
    """Return a lemmatized version of the title."""
    words = word_tokenize(title)
    lemmas = lemmatize_words(words)
    return ' '.join(lemmas)


def get_stopwords() -> List[str]:
    stopwords_en = stopword_sets.words('english')
    stopwords_fr = stopword_sets.words('french')
    stopwords_sp = stopword_sets.words('spanish')
    stopwords_all = stopwords_en + stopwords_fr + stopwords_sp
    return stopwords_all


def remove_footnote_symbols(title: str) -> str:
    """Remove footnote symbols in the title like * and 1."""
    title = re.sub(r'([a-z]+)[12]', r'\1', title)
    if title.endswith('*'):
        return title[:-1]
    elif title.endswith(' 1'):
        return title[:-2]
    else:
        return title


def normalise_acronyms(title: str) -> str:
    """Remove dots in acronyms (A.D. -> AD , U.S.A. -> USA)"""
    match = re.search(r'\b((\w\.){2,})', title)
    if match:
        acronym = match.group(1)
        normalised_acronym = acronym.replace('.', '')
        title = title.replace(acronym, normalised_acronym)
    return title


def resolve_apostrophes(title: str) -> str:
    """Remove 's from words."""
    title = title.replace("‘", "'")
    title = re.sub(r"(\w)'s\b", r'\1', title)
    return title


def remove_punctuation(title: str) -> str:
    """Remove all non-alpha-numeric characters except whitespace and hyphens"""
    title = re.sub(r'[^\w -]', ' ', title)
    return title


def collapse_multiple_whitespace(title: str) -> str:
    """Reduce multiple whitespace to a single whitespace, e.g. '  ' -> ' '. """
    title = re.sub(r' +', ' ', title)
    return title.strip()


def normalise_title(title: str) -> str:
    """Apply all normalisation rules to a title."""
    title = remove_footnote_symbols(title)
    title = normalise_acronyms(title)
    title = resolve_apostrophes(title)
    title = remove_punctuation(title)
    # For IMR articles, 'Book Review' is a 'stop phrase'
    title = title.replace('Book Review', '')
    title = collapse_multiple_whitespace(title)
    # Lower casing is needed because article titles use uppercase initials for most content words
    title = lemmatize_title(title.lower())
    # lower case 'united states' is lemmatized to 'united state', so fix that
    # this issue no doubt plays up for other names, but 'united states' is so frequent
    # that it warrants its own fix.
    title = re.sub(r'\bunited state\b', 'united states', title)
    return title.lower()


def demonstrate_normalisation(df, max_titles: int = 25) -> None:
    titles = list(df.article_title)
    for title in titles[:max_titles]:
        print('Original:', title)
        title = normalise_title(title)
        print('Normalised:', title)
        print()


def make_title_unigram_term_list(title: str,
                                 stopword_list: List[str] = None,
                                 normalise: bool = False):
    """Transform a title string into a list of single word terms."""
    if not title:
        # is title is None or empty, return empty term list
        return []
    # normalise the title using the steps described above
    if normalise:
        title = normalise_title(title)
    # .split(' ') splits the title into chunks wherever there is a whitespace
    terms = title.split(' ')
    # remove stopwords
    terms = [term for term in terms if term not in stopword_list]
    return terms


def get_unigram_freq(titles: List[str], normalise: bool = True, remove_stop: bool = False) -> Counter:
    uni_freq = Counter()
    stopwords_all = get_stopwords()
    for title in titles:
        # normalise the title using the steps described above
        if normalise:
            title = normalise_title(title)
        # .split(' ') splits the title into chunks wherever there is a whitespace
        terms = title.split(' ')
        if remove_stop:
            terms = [term for term in terms if term not in stopwords_all]
        # count each term in the sentence, excluding 'empty' words
        uni_freq.update([term for term in terms if term != ''])
    return uni_freq


def get_bigram_freq(titles: List[str], normalise: bool = True, remove_stop: bool = False) -> Counter:
    bi_freq = Counter()
    stopwords_all = get_stopwords()
    for title in titles:
        # normalise the title using the steps described above
        if normalise:
            title = normalise_title(title)
        # .split(' ') splits the title into chunks wherever there is a whitespace
        terms = title.split(' ')
        # get all pairs of subsequent title words
        bigrams = list(zip(terms[:-1], terms[1:]))
        # remove all bigrams for which the first or second word is a stopword
        if remove_stop:
            bigram_terms = [' '.join(bigram) for bigram in bigrams if
                            bigram[0] not in stopwords_all and bigram[1] not in stopwords_all]
        else:
            bigram_terms = [' '.join(bigram) for bigram in bigrams]
        # count the occurrence of each bigram
        bi_freq.update(bigram_terms)
    return bi_freq


def get_unigram_odds(titles_1: List[str], titles_2: List[str],
                     normalise: bool = True, remove_stop: bool = False) -> DataFrame:
    """
    calculate the odds that a uni-gram term is draw from titles_1 instead of titles_2
    using add-one smoothing for terms that occur in one set of titles but not in another
    """
    uni_freq_1 = get_unigram_freq(titles_1, normalise=normalise, remove_stop=remove_stop)
    uni_freq_2 = get_unigram_freq(titles_2, normalise=normalise, remove_stop=remove_stop)
    return get_frequency_odds(uni_freq_1, uni_freq_2)


def get_bigram_odds(titles_1: List[str], titles_2: List[str],
                    normalise: bool = True, remove_stop: bool = False) -> DataFrame:
    """
    calculate the odds that a bi-gram term is draw from titles_1 instead of titles_2
    using add-one smoothing for terms that occur in one set of titles but not in another
    """
    bi_freq_1 = get_bigram_freq(titles_1, normalise=normalise, remove_stop=remove_stop)
    bi_freq_2 = get_bigram_freq(titles_2, normalise=normalise, remove_stop=remove_stop)
    return get_frequency_odds(bi_freq_1, bi_freq_2)


def get_frequency_odds(term_freq_1: Counter, term_freq_2: Counter) -> DataFrame:
    """
    calculate the odds that a term is draw from frequency distribution 1 instead of distribution 2
    using add-one smoothing for terms that occur in one distribution but not in another
    """
    odds_1 = {}

    # vocabulary size is the number of distinct terms
    vocabulary = set(list(term_freq_1.keys()) + list(term_freq_2.keys()))
    vocabulary_size = len(vocabulary)

    # add vocabulary size to compensate for add-one smoothing
    total_freq_1 = sum(term_freq_1.values()) + vocabulary_size
    total_freq_2 = sum(term_freq_2.values()) + vocabulary_size

    for term in vocabulary:
        freq_1 = term_freq_1[term] + 1  # add-one smoothing for terms that only occur in titles_1
        freq_2 = term_freq_2[term] + 1  # add-one smoothing for terms that only occur in titles_2
        prob_1 = freq_1 / total_freq_1
        prob_2 = freq_2 / total_freq_2
        odds_1[term] = prob_1 / prob_2

    return pd.DataFrame({
        'term': [term for term in vocabulary],
        'freq': [term_freq_1[term] for term in vocabulary],
        'odds': [odds_1[term] for term in vocabulary],
    })


def color_odds(odds: float, boundary: int = 2):
    """
    Takes a scalar and returns a string with the css color property set to green
    for positive odds above the boundary, blue for negative odds below the boundary
    and black otherwise.
    """
    if odds > boundary:
        color = 'green'
    elif odds < 1 / boundary:
        color = 'blue'
    else:
        color = 'black'
    return 'color: %s' % color


def highlight_odds(row, column_name, boundary=2):
    """
    color row values based on odds.
    """
    term_color = color_odds(row[column_name], boundary)
    return [term_color for _ in row]


def extract_ngram_freq(titles):
    # count frequencies of individual words
    stopwords_all = get_stopwords()
    uni_freq = Counter()

    for title in titles:
        # normalise the title using the steps described above
        title = normalise_title(title)
        # .split(' ') splits the title into chunks wherever there is a whitespace
        terms = title.split(' ')
        # remove stopwords
        terms = [term for term in terms if term not in stopwords_all]
        # count each term in the sentence, excluding 'empty' words
        uni_freq.update([term for term in terms if term != ''])

    for term, freq in uni_freq.most_common(25):
        print(f'{term: <30}{freq: >5}')


def extract_bigrams(titles, stopwords):
    bigram_measures = BigramAssocMeasures()
    # split all titles into a single list of one-word terms
    words = [word for title in titles for word in title.split(' ')]
    # create a bigram collocation finder based on the list of words
    finder = BigramCollocationFinder.from_words(words)
    # Remove bigrams that occur fewer than five times
    finder.apply_freq_filter(5)
    # select all bigrams that do no include stopwords
    bigrams = []
    for bigram in finder.nbest(bigram_measures.pmi, 1000):
        if bigram[0] in stopwords or bigram[1] in stopwords:
            continue
        bigrams.append(bigram)
    return bigrams


def mark_bigrams(title, bigrams):
    for bigram in bigrams:
        if ' '.join(bigram) in title:
            title = title.replace(' '.join(bigram), '_'.join(bigram))
    return title


def get_usas_label_map():
    usas_hierarchy_file = '../data/semtags_subcategories.txt'
    usas_label_map = {}
    with open(usas_hierarchy_file, 'rt') as fh:
        for line in fh:
            code, label = line.strip().split('\t')
            usas_label_map[code] = label
    return usas_label_map


def get_usas_general_labels():
    usas_label_map = get_usas_label_map()
    general_labels = [usas_label_map[code] for code in usas_label_map if len(code) == 1]
    return general_labels


def parse_usas_specific_code(code, usas_label_map):
    while len(code) > 1:
        if code in usas_label_map:
            return usas_label_map[code]
        code = code[:-1]


def parse_usas_general_code(code, usas_label_map):
    # print('CODE:', code)
    for i in range(1, len(code) + 1):
        # print(f'CODE: {i}', code[:i])
        if code[:i] in usas_label_map:
            return usas_label_map[code[:i]]


def parse_usas_codes(codes, usas_label_map, level='specific'):
    parse_usas_code = parse_usas_specific_code if level == 'specific' else parse_usas_general_code
    labels = []
    for code in codes:
        if '/' in code:
            for code_alt in code.split('/'):
                labels += [parse_usas_code(code_alt, usas_label_map)]
        else:
            labels += [parse_usas_code(code, usas_label_map)]
    return labels


def parse_usas_line(line, usas_label_map):
    parts = re.split(' +', line.strip())
    line_num, word_num, pos, word = parts[0:4]
    assert (line_num.isdigit())
    usas_code = ' '.join(parts[4:])
    codes = parts[4:]
    return {
        'line': line_num,
        'pos': pos,
        'word': word,
        'code': usas_code,
        'labels_specific': parse_usas_codes(codes, usas_label_map, level='specific'),
        'labels_general': parse_usas_codes(codes, usas_label_map, level='general')
    }


def get_usas_line_data():
    usas_file = '../data/main-review-article-titles-ucrel.txt'
    usas_label_map = get_usas_label_map()
    line_data = defaultdict(list)
    with open(usas_file, 'rt') as fh:
        _top_line = next(fh)
        for li, line in enumerate(fh):
            data = parse_usas_line(line, usas_label_map)
            line_data[data['line']].append(data)
    return line_data


def get_title_usas_label_counts():
    general_labels = get_usas_general_labels()
    line_data = get_usas_line_data()
    titles = []
    title_label_counts = []
    for li, line in enumerate(line_data):
        words = [word_data['word'] for word_data in line_data[line]]
        title = ' '.join(words)
        labels = [label for word_data in line_data[line] for label in set(word_data['labels_general'])]
        label_count = Counter(labels)
        label_count = [label_count[label] for label in general_labels]
        titles.append(title)
        title_label_counts.append(label_count)
    return title_label_counts


def generate_uses_top_word_frequencies(top_n: int = 30):
    general_labels = get_usas_general_labels()
    label_word_count = defaultdict(Counter)
    line_data = get_usas_line_data()
    # count how often each word is labelled with each general category
    for line in line_data:
        for word_data in line_data[line]:
            for label in word_data['labels_general']:
                label_word_count[label].update([word_data['word']])
    data_list = []
    # list the top N most frequent words per category
    for label in general_labels:
        # print(f'\n{label}\n--------------------')
        for word, count in label_word_count[label].most_common(top_n):
            data_list.append({'label': label, 'word': word, 'count': count})
            # print(f'{label: <30}{word: <25}{count: >5}')
    # write the top N lists to a CSV file
    label_df = pd.DataFrame(data_list)
    label_df.to_csv('../data/ucrel_usas-general_labels-word_freq.csv')
