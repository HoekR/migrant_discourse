# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 16:12:16 2017

@author: root
"""
import os
import nltk
from bs4.dammit import UnicodeDammit
from collections import Counter
from unicodecsv import DictReader, DictWriter
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from nltk.corpus import stopwords

stopwords = stopwords.words('english')

def from_files():
    basedir = "/Users/rikhoekstra/surfdrive/Shared/Documents/NIOD2017/International_MIgration"
    toread = [fl for fl in os.listdir(basedir)]
    result = []
    
    for fl in toread:
        infl = open(os.path.join(basedir, fl), 'rU')
        txt = infl.read()
        recs = txt.split("\n\n")[1:]
        for r in recs:
            rec = r.split('\n')
            res = {}
            for l in rec:
                item = l.split(' - ')
    #            print item
    #            for item in splitted:
    #           import pdb; pdb.set_trace()
                if len(item)>1  and item[0].strip() in ['AU', 'TI', 'PY', 'JO']:
                    res[item[0].strip()] = item[1].strip()
            result.append(res)
    
    flout = open('wileyrecs.csv', 'w')
    
    w = DictWriter(flout, ['AU', 'TI', 'PY', 'JO'])
    w.writeheader()
    w.writerows(result)
    flout.close()
    print('written: ', flout.name)
    return result

def classify(result, start=1960, end=2020, step=10):
    for i in result:
        if i == {}:
            result.remove(i)
    ks = {"{i}".format(i=i):[] for i in range(start, end, step)}
    for i in result:
        try:
            x = [k for k in ks.keys() if int(i["PY"]) in range(int(k), int(k)+step)][0] 
        except IndexError:
            print (i)
        ks[x].append(i)
    return ks
    
def freqdst(ks, stopwords=stopwords, leaveout=[]):
    stopwords.extend(leaveout)
    tokenizer = nltk.word_tokenize
    txtout = dict.fromkeys(ks.keys())
    for k in ks.keys():
        txt = ' '.join([i['TI'] for i in ks[k]])
        txt = txt.lower()
        try:
            tok = tokenizer(UnicodeDammit(txt).unicode_markup)
        except UnicodeEncodeError:
            pass # dan niet
        tok = [t for t in tok if t not in stopwords]
        tok = [t for t in tok if len(t)>2]
        txtout[k] = tok
    return txtout

def allwrds(f):
    wrds = []
    for k in f.keys():
        if f != None:
            wrds.extend(f[k])
    return wrds
    
def termfreq(f, key):
    fc = Counter(allwrds(f))
    ff = Counter(f[key])
    tf = {term:(ff[term]/float(fc[term]))*ff[term] for term in ff}
    return tf
    

def wrdcloud(txt):
    wordcloud = WordCloud(font_path='/Library/Fonts/Verdana.ttf',
                          relative_scaling = 1.0,
                          stopwords = {'the', 'in', 'to', 'a', 'of', 'for', ':', 'and', ',', '?', 'with'})
    wordcloud.generate_from_text(txt)
    plt.imshow(wordcloud)
    plt.axis("off")


def simplerun(fl, stopwords=stopwords):
    results = {}
    fl = open(fl)
    rd = DictReader(fl, encoding='utf-8')
    result = [row for row in rd if row['AU']!='' ]
    for item in result:
        item['TI'] = item['TI'].lower().replace('(book)', '')
    ks = classify(result, end=2020)
    f = freqdst(ks, stopwords=stopwords,leaveout=['book'])
    for k in ks:
        tf = termfreq(f, k)
        results[k] = tf
    return results

def simplecloud(fl, stopwords=stopwords):
    wordclouds = {}
    fl = open(fl)
    rd = DictReader(fl, encoding='utf-8')
    result = [row for row in rd if row['AU']!='' ]
    for item in result:
        item['TI'] = item['TI'].lower().replace('(book)', '')
    ks = classify(result, end=2020)
    f = freqdst(ks, stopwords=stopwords)
    for k in ks:
        wordcloud = WordCloud(font_path='/Library/Fonts/Verdana.ttf',
                              relative_scaling=1.0,
                              stopwords=stopwords)
        tf = termfreq(f, k)
        wordcloud.generate_from_frequencies(tf)
        wordclouds[k] = wordcloud
    return wordclouds

def compare_wdcloud(fls, stopwords=stopwords):
    """for title dbs with 'TI' and 'AU' fields"""
    wordclouds = {}    
    for fl in fls:
        wordclouds[fl] = {}
        fl = open(fl)
        rd = DictReader(fl, encoding='utf-8')
        result = [row for row in rd if row['AU']!='' ]
        for item in result:
            item['TI'].lower().replace('(book)', '')
        ks = classify(result, end=2020)
        f = freqdst(ks, stopwords=stopwords)
        for k in ks:
            wordcloud = WordCloud(font_path='/Library/Fonts/Verdana.ttf',
                                  relative_scaling=1.0,
                                  stopwords=stopwords)
            tf = termfreq(f, k)
            wordcloud.generate_from_frequencies(tf)
            wordclouds[fl][k] = wordcloud


