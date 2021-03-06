# Discourse Coalitions Migration Management

## Translating Research Questions to methodological questions

### Exploring archives and formulating research Questions

Explorations of the archives of Günther Beyer (ARCH03193 – 31, 32 and 33-40) make clear that he was an important participant in the foundation of PICMME (_Provisional Intergovermental Committee for the Movement of Migrants_) and REMP (_Research Group for European Migration Problems_) in 1950. These are respectively a political institution (later evolved into the ICEM - _Intergovernmental Committee for European Migration_) and a research group for migration, but they were both connected from the start as a Dutch-German connection, with some connections to France (Sauvy) and the USA (Walter).
Whereas this makes clear that there is a connection between politics and research, the extent is not clear. Also involved were later sociologists that wrote about and were influential in Dutch emigration. Another indication of the close connection was the association between Haveman, the Dutch 'commissaris voor de emigratie' and later secretary (XXX klopt dit??) of the ICEM and the sociologists. (For more background see Van Faassen, _Emigratie en Polder_, Chapter 3, 121-171). This marks a beginning of what we presumed to grow into a discourse coalition (see the main text for explanations). The main research questions were, therefore, whether this discourse coalition was actually established, who it consisted of and what its influence was on the political and scientific debate.

In order to answer these research questions, they have to be translated into methodological questions, more specifically in datasets that are usable to answer the questions. It soon appeared that there were two somewhat disconnected research questions that call for a different methodological approach.

### 1. Constructing a Technocratic Network

The first question is about the existing of a network of connected technocrats, politicians, and scientists in the field of migration. For this, we used the publications of the REMP research group Beyer had constituted in the early 1950s. Its conferences and publications brought together scientists, politicians, and technocrats and many publications were either financed by political institutions such as the Dutch ministry of Foreign Affairs. In the REMP publications, technocrats such as Haveman wrote introductions for the REMP publications they had commissioned.

This is indicative of the relations between the scientists and technocrats. We explore these relations by making a (network) graph out of all REMP titles, both from the REMP bulletin and the REMP publications. Publications and persons are different nodes in the graph where they are connected by edges and we have separate roles (edge types) for authors, editors and writers of an introduction and of a preface. The person have types  (XXX rather should have, as this is not yet in the data) indicating whether they are technocrats or scientists. This enables us to make a network graph of the discourse coalition and its evolution over time.

### 2. Analysing Topical Shifts in Migration Publication via Title Words

The second part of the research question is the content of the migration management discourse and its change over time. The titles in the REMP publications were not enough in quantity and in time span to be able to determine topics in research. For this, we needed a long running series of publications that was closely connected to the people of the network of the discourse coalition.

The first effort was to harvest titles from the site of WorldCat ([worldcat.org](https://worldcat.org)), that allows for creating tagclouds of the selected publications (see for example http://www.worldcat.org/identities/lccn-n50-55088/ for a cloud of the _Intergovernmental Committee for European Migration_ (ICEM)). Upon closer inspection, however, this tag cloud is based on the assigned keywords from the catalog (called 'associated subjects'), that is not so much an expression of the titles in the database as of the librarians from 'more than 10,000 libraries from over the world' who assigned the (available) keywords from their cataloguing system. This introduces a secondary mask of interpretation on top of the titles relevant for the research question.

The _International Organization for Migration_ (IOM, successor to ICEM and now a United Nations organization) has a list of journals they use for migration studies trend analysis. Most started after 2000 and the earliest in 1985. Two journals, _International Migration_ (from 1961) and the _International Migration Review_ (from 1966) have a longer history. For our purposes, the most suitable collection is _International Migration_
(http://onlinelibrary.wiley.com/doi/10.1111) [XXX remark something about harvesting titles separately recently and ending up with almost the same dataset?], a journal running from 1961 till today, for which a complete list of titles was available online.

_International Migration_ is the successor to and a merger of journals _REMP Bulletin_ and the _Migration_ (also known under its Spanish name _Migración_). REMP bulletin was the journal of the REMP we wrote about above. As _International Migration_ was its successor, we included the titles of the REMP publications in our title analysis. [XXX remark something about IMR and analysis, depending on what we will do with it]

We chose to use a list of titles, rather than the full-text of this set of publications, not only because there is no such set available and analyzing it brings many new problems, but also because in our view titles can be viewed as a short summary of the content. After all, authors use their title to catch the interest or curiosity of their prospective readers by catching the essence of their text and also by using scientific terms that are in fashion.

The analysis is documented in [analysis notebook](../notebooks/publication-title-analysis.ipynb)
