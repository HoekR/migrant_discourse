# Discourse Coalitions on Migration Management

Code for the digital history contribution about discourse coalitions.

Authors: Marijke van Faassen, Rik Hoekstra, Marijn Koolen (KNAW - Huygens ING)

### Topic

**International migration management and technocracy**

The scholarly debate on international migration has been characterized over the past 30 years by a focus on globalization and a paradigm shift to the study of migration management. The key actors in migration management are the nation states and also the international meetings and organisations consisting of trained experts. They have become more and more the subject of current discourses around the legitimacy of technocratic governance. In this article we will historicize the concept of migration management and investigate the connections between technocratic experts and one of today’s biggest players in the international field, albeit a fairly contested one: the International Organisation for Migration (IOM) by operationalizing the concept of discourses coalitions.

##  Publication Layers

This publication has three layers:

1. The narrative layer containing the historicali argumentation,
2. The hermeneutic or processing layer containing the data processing steps and their elaboration,
3. The data layer describes the digital documents used in processing.

### Narrative Layer

The current activities of the IOM with regard to the regulation of migrant flows is not undisputed. In particular, the ‘voluntary’ return programs appear to be subject to criticism. Geiger and Koch (2018) conceptualize the ‘intergovernmental’ IOM as a ‘world organization’ as IOM has relations with both state and non-state actors, such as NGOs or civil society. This, they argue, makes it possible to analyze which actors participate in the decision-making process, how they participate, and with what authority. Although they suggest to describe IOM’s history from the start in 1951 (with the constitution of its predecessor PICMME), in fact they directly jump to the mid 1980s, thus leaving its historical roots understudied (but see Parsanoglou and Tourgeli 2017), and especially IOM’s technocratic character (p.39). Especially the constitutive years of ICEM are key to understanding how and which actors from both science and politics were able to be of influence on ICEM’s decision-making processes. By using the concept of discourse coalitions - defined by Wagner (as cited in Raphael 2012) as constellations at any given time in which social scientists develop ideas ‘that strengthen the arguments of a group of actors in the political system, whose policies might, in turn, support the standing of these scientists in academia’,  we are able to lay bare networks of technocrats (on basis of their publications) shaping migration management interactively with national governments.

#### Research Questions

Main RQ 1: What is the connection between the Intergovernmental Committee for European Migration (ICEM) (and its successor IOM) and the Researchgroup for European Migration Problems (REMP); can REMP be seen as the informal discourse coalition which formed the nexus between science and politics in what nowadays is called ‘migration management’. How did this supposed discourse coalition develop through time and how can this be explained?

Sub-questions:
1. Who were the key scientists involved, and who were the key political actors?

2. How were they connected to the key political actors and institutions mentioned above? ([RQ2 elaboration](./documents/RQ2Methodology.md))

3. How robust are our choices for processing and visualising the data?


##  Hermeneutic / Processing Layer

In this layer we elaborate the data processing and analysis. The discussion comprises:
- The translation of the research question to queries of the data sources using the Data Scopes framework (Hoekstra & Koolen 2019).
- The analysis and combination of various data sources to (partial) answers to the research questions
- The choices for making network visualisations
- We include a robustness analysis of our chosen methods.
  - The key point is to demonstrate how different choices for visualising the topical analysis and the actor networks affect the visualisations and what they highlight.
  - We include a dynamic network visualisation that redraws the network for a sliding 10-year window over the entire period. In the notebook, readers can change the size of the window to show how different period lengths affect the networks.
- Which ‘tools’ did we use (notebooks, scripts, visualization software etc)

### Process
We put effort into finding additional series. We decided to also study the International Migration Review series and analyse overlap /differences between editors, authors, topics

###  Methodology

#### Assumptions

Worldcat data problems:

- Different libraries make different choices in creating metadata and keywords
- Metadata is shaped by ideologies of organisational structures

We use network analysis to interpret the discourse structure. How do we analyse these networks? How do we interpret them? How do we compare the networks as we have them against alternative choices? And against alternative outcomes (what if the resulting networks were different)? What were our expectations for what kinds of things the networks could reveal?

From the Modeling Society paper:

> In this paper I will start to unravel some of these discourse coalitions, particularly those concerned with international migration. I will do this by providing a genealogy (following  Raphaels configuration or periodization) of both the Dutch national migration system and  one of today’s biggest players in the international field, albeit a fairly contested one: the  International Organisation for Migration (IOM). Both put down their roots before the Second  World War but were legally founded in 1951-1952. In a general overview I will briefly outline their aims, how they related to each other, and how ‘sensitive’ their key actors were with  regard to issues such as democracy and the legitimacy of their policy. Then I will zoom in on  a group of international scholars that joined forces in the Netherlands in 1951 as the  Research Group for European Migration Problems (REMP). I will argue that this group was  the informal discourse coalition which formed the nexus between science and politics in  what nowadays is called ‘migration management’. I will address two key questions: “Who  were the key scientists involved?” and “How were they connected to the key political actors  and institutions mentioned above?”.  Finally, I will briefly reflect on what Raphael has called  ‘secondary scientization’. This is the phrase used from the 1970s and 1980s onwards, during  a period when a general critical awareness and response towards social scientific knowledge  was growing. These were also the years of Foucault’s lectures on ‘Security, Territory,  Population’, which inspired several ‘Governmentality’ researchers to critically reflect upon  IOM’s current promotion of ‘border management’?.7  Do these years mark the shift to a new  discourse and perhaps to a new coalition around this specification of migration management  which could explain the disputes around IOM today’?

### Selection

- Why and how do the data support our story
- The necessity of combining analog and digital research

For the analysis we used the articles published in the REMP publications, the REMP Bulletin (1951-1962) and the International Migration bulletins (1961-1990). For the word clouds and topical analysis, we use the titles of the articles. For the network analysis of actors, we extracted the names of authors, editors, funders and others from prefaces and introductions to journal editions.

Selection of sources
- To investigate the discourse coalitions, we started from the focus of Gunther Beyer and found several journals on international migration in which he played a central role.
- Choices and selection of information layers extracted from sources
- Discuss the completeness of publications and consequences of missing publications for the structure of the networks and for the word clouds
- Most relevant materials are not digitally available (?)
- The metadata was extracted from WorldCat

### Notebooks

This layered publication contains three Jupyter notebooks

1. [Data Selection and Modelling](./notebooks/Data-Selection-Modelling.ipynb):
    - Data gathering, inspection (iterative, switching between quantitative and qualitative), selection criteria
    - Selection: REMP + Studies (manual), IM + IMR (crawl of ToC of issues)
    - Extraction: Metadata (title, author, affiliation, year, journal, article type, …)
    - Inspection:
        - Publication date (missing issues)
        - Authors (authorless articles)
        - Article type (editorial articles, review articles, research articles)

2. [Publication title analysis](./notebooks/publication-title-analysis.ipynb):
    - Selection
        - REMP and IM titles
        - IMR book reviews
        - IMR articles
    - Modelling: topics as unigram + bigram words, countries and nationalities
    - Normalization: stopwords, case, lemmatization
    - Classification: countries, emigration vs immigration …
    - Visualisation: frequency lists, word clouds
3. [Network analysis](./notebooks/NetworksResearchQuestions.ipynb):
    - Selection: REMP + Studies
    - Modelling: academics, public administrators, publication roles
    - Linking: publication roles
    - Classification: academics, public administrators
    - Visualisation


### Data Layer

In the data layer we describe the resources we have used, including both digital and analogue resources.

Data sets

Our research resulted in the construction of two data sets, each based on metadata and information extracted from close reading of one or more journal series on international migration.

Data set 1 (for the network analysis):
- REMP publications 1-20 (books, 1952-1974)
- REMP Bulletins (1952-1962)
- REMP Bulletins Supplements (1954-1984)
- Studies over Nederlandse Migratie (1958-1962)
- Studies in Social Life (1953-1974, only migration studies)
- REMP Board
- ICEM personnel/director general & under-director general? See: [https://www.iom.int/dg-and-ddg](https://www.iom.int/dg-and-ddg)


Data set 2 (for the content analysis of the discourse):

- REMP (Bulletins + books) + Studies (1951-1984)
- International Migration Magazine (all articles published in the period 1961-2000)
- International Migration Review (1964-2000)
    - Book reviews
    - Articles


These are based on the following WorldCat identities:
- REMP: https://worldcat.org/identities/lccn-n50070935/
- ICEM: https://worldcat.org/identities/lccn-n50055088/
- IOM: https://worldcat.org/identities/lccn-no90018047/

## References

Faassen, M. van, & Hoekstra, F. G. (2017). Modelling Society through Migration Management: Exploring the role of (Dutch) experts in 20th century international migration policy. . Paper presented at Government by Expertise, Amsterdam, Netherlands.

Geiger M & Koch M (2018) “World Organizations in Migration Politics: The International Organization for Migration”. Journal of International Organizations Studies (JIOS) 9(1): 23-42

Hoekstra, F. G., Koolen, M., & van Faassen, M. (2018). Data scopes: towards transparent data research in digital humanities. Digital Humanities 2018 Puentes-Bridges.

Koolen, M., Kumpulainen, S., & Melgar-Estrada, L. (2020, March). A Workflow Analysis Perspective to Scholarly Research Tasks. In Proceedings of the 2020 Conference on Human Information Interaction and Retrieval (pp. 183-192).

Parsanoglou,  D., Tourgeli, G. (2017). “The Intergovernmental Committee for European Migration (ICEM) as part of the post-WWII ‘world-making’” in: Peoples and Borders : Seventy Years of Migration in Europe, from Europe, to Europe \[1945-2015\], edited by Elena Calandri, et. al., Nomos Verlagsgesellschaft, ProQuest Ebook Central, http://ebookcentral.proquest.com/lib/kb/detail.action?docID=5519170.

Raphael, Lutz (2012), ‘Embedding the Human and Social Sciences in Western Societies, 1880-1980. Reflections on Trends and Methods of Current Research’, Brückweh, K., Schumann, D., Wetzell, R. F., Ziemann, B. (eds.), Engineering Society. The Role of the Human and Social Sciences in Modern Societies, 1880-1980, Palgrave Macmillan 2012, 41-56.

