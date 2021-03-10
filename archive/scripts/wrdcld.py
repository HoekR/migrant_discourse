# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 16:41:16 2017

@author: rikhoekstra
"""
import os
import nltk
#from unicodecsv import DictReader
#from wiley import *
from nltk.corpus import stopwords

stopwords = stopwords.words('dutch')
tokenizer = nltk.word_tokenize


dl = [row for row in r]

ts = {"{i}".format(i=i):[] for i in range(1880, 2010, 10)}

for i in dl:
    try:
        x = [k for k in ts.keys() if int(i['PY']) in range(int(k), int(k)+10)][0]
        ts[x].append(i)
    except ValueError:
        print (i)

txtout = dict.fromkeys(ts.keys())

for k in ts.keys():
    txt = ' '.join([i['TI'] for i in ts[k]])
    txt = txt.lower()
    try:
        tok = tokenizer(UnicodeDammit(txt).unicode_markup)
    except UnicodeEncodeError:
        pass # dan niet
    tok = [t for t in tok if t not in stopwords]
    tok = [t for t in tok if len(t)>2]
    txtout[k] = tok

for k in txtout.keys():
    if txtout[k] == []:
        del(txtout[k])


wordclouds = {}
ks = txtout
for k in ks:
    wordcloud = WordCloud(font_path='/Library/Fonts/Verdana.ttf',
                          relative_scaling=1.0,
                          stopwords=stopwords)
    tf = termfreq(txtout, k)
    wordcloud.generate_from_frequencies(tf)
    wordclouds[k] = wordcloud

for key in enumerate(wordclouds.keys()):
    plt.figure(key[0])
    plt.imshow(wordclouds[key[1]])
    plt.axis('off')
    plt.savefig(os.path.join(basedir, 'wc_%s.png' % key[1]))
