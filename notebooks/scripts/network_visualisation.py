from collections import defaultdict, Counter
import networkx as nx
import altair as alt
import nx_altair as nxa
from community import community_louvain
from .data_wrangling import *
from .network_analysis import *
from .graph_community import community_layout
from scripts.graphs_and_tables import entity_records, cat_p_df, record, relationship_records, entity_category

roled = {'author':['article_author1_surname','article_author2_surname'],
 'preface_author':['preface_author1_surname','preface_author2_surname'],
 'intro_author':['intro_author1_surname','intro_author2_surname'],
 'executor':['executor_org'],
 'funder':['funder'],
 'client':['client'],
 'editor':['editor_surname'],
 'unknown':['']}
nms = [get_entity_name(entity=record) for record in entity_records]
surnms = [record['prs_surname'] for record in entity_records]
remp_entities = cat_p_df.loc[cat_p_df.fullname.isin(nms)]
remp_entities_comp = cat_p_df.loc[cat_p_df.prs_surname.isin(surnms)]
record_entities = defaultdict(list)
entity_count = Counter()
entity_role_count = Counter()
entities = extract_record_entities(record)
nodelist = []

for ri, record in enumerate(relationship_records):
    record_entities[ri].append(entities)
    entity_count.update([entity['entity_name'] for entity in entities if 'entity_name' in entity])
    entity_role_count.update([entity['entity_role'] + ' ' + entity['entity_name'] for entity in entities if 'entity_name' in entity])
    for entity in entities:
        if entity['entity_type'] == 'person':
            entity['entity_type'] = get_entity_category(entity, entity_category)

for rentity in record_entities:
    nodelist.extend(make_nodes(record_entities[rentity][0]))
nodelist = list(set(nodelist))
revnodelist = {}
rempgraph = nx.Graph()
for node in enumerate(nodelist):
    rempgraph.add_node(node[0], id=node[0], name=node[1])
    revnodelist[node[1]]=node[0]

linklist = []
counter = Counter()
for rentity in record_entities:
    links, cntr = make_link_from_entity(record_entities[rentity][0], revnodelist, rempgraph)
    linklist.extend(links)
    counter.update(cntr)

communities = {}
for i in cat_p_df.organisation.unique():
     communities[i] = list(cat_p_df.loc[cat_p_df.organisation==i].fullname)

periods = {
    1950:{'start': 1950, 'end': 1959},
    1960:{'start': 1960, 'end': 1969},
    1970:{'start': 1970, 'end': 1985},
}

grphdict = {}

for period in periods:
    period = periods[period]
    pn = period['start']
    periodgraph = generate_graph()
    for record in relationship_records:
        record['year'] = int(record['year'])
    for ri, record in enumerate(sorted(relationship_records, key = lambda x: x['year'])):
        record['year'] = int(record['year'])
        if record['year'] < period['start'] or record['year'] > period['end']:
            continue
        entities = extract_record_entities(record)
        for entity in entities:
            if entity['entity_type'] == 'person':
                entity['entity_type'] = get_entity_category(entity, entity_category)
        named_entities = [entity for entity in entities if 'entity_name' in entity]
        add_entities(periodgraph, named_entities)
        add_record_links(periodgraph, named_entities)
    grphdict[pn] = periodgraph

periodcentralities = {}
nodelists = {}
for pn in grphdict:
    periodcentralities[pn] = nx.eigenvector_centrality(grphdict[pn])
    nodelists[pn] = [n for n in grphdict[pn].nodes()]

commonnames = {}

window_size = 2

seq = list(nodelists.keys())
for i in range(len(seq) - window_size + 1):
    w = seq[i: i + window_size]
#     {e:set(nodelists[e]) for e in }
    for item in w:
        if item not in commonnames.keys():
            commonnames[item] = list(set(nodelists[w[0]]) & set(nodelists[w[1]]))

for i in commonnames:
    commonnames[i].append('Haveman, B.W.')

#this method factors out commonalities for the graphs below
def period_graph(pn, grphdict=grphdict, periodcentralities=periodcentralities, commonnames=commonnames):
    periodgraph = grphdict[pn]

    for f in periodgraph.nodes():
                # comty = periodgraph.nodes[f].get('community')
                # comty = ''.join([c[0] for c in comty])
                if f in commonnames[pn]:
                    label = f
                else:
                    label = ''
                periodgraph.nodes[f].update({#"community" : comty,
                                    # "edgecolor": colors.get(comty) or 'purple',
                                    "centrality" : periodcentralities[pn][f]*4,
                                    "name" : f,
                                    "label" : label
                                   })

    for f in periodgraph.edges():
        for i, c in communities.items():
             if f[0] and f[1] in c:
                comty = periodgraph.edges[f].get('community') or ''
                comty = ', '.join([comty,i])
                # comty = ''.join([c[0] for c in comty])
                periodgraph.edges[f].update({"community" : comty,
                                    })

    for f in periodgraph.edges():
        comty = periodgraph.edges[f].get('community') or []
        comty = ''.join([c[0] for c in comty])
        periodgraph.edges[f].update({"community" : comty})
    partition = community_louvain.best_partition(periodgraph)
    pos = community_layout(periodgraph, partition)

    return periodgraph, pos




chartdict = {}
for period in enumerate(grphdict.keys()):
    n = period[0]
    pn = period[1]
    periodgraph, pos = period_graph(pn)

    chart = nxa.draw_networkx(
            G=periodgraph,
            pos=pos,
            node_size='centrality',
            node_color='entity_type',
            edge_color='community',
            cmap='category20',
            #edge_cmap='category10',
            node_tooltip=['name'],
            node_label='label',
            font_color="black",
            font_size=11,
        )
    start = periods[pn]['start']
    end = periods[pn]['end']
    chart.title = f"REMP network {start}-{end}"
    chart.properties(
        height=600,
        width=800
    )
    chartdict[n] = chart

vconcat = alt.vconcat(chartdict[0], chartdict[1], chartdict[2])


import hvplot.networkx as hvnx
import holoviews as hv

chartdict2 = {}
charts=None
for period in enumerate(grphdict.keys()):
    n = period[0]
    pn = period[1]
    periodgraph, pos = period_graph(pn)
    labels = {node: node for node in periodgraph.nodes() if node in commonnames[pn]}
    start = periods[pn]['start']
    end = periods[pn]['end']
    chart.title = f"REMP network {start}-{end}"
    chart = hvnx.draw(G=periodgraph,
                      pos=pos,
                      with_labels=True,
                      labels=labels,
                      node_size=hv.dim('centrality')*200,
                      node_color='entity_type',
                      edge_color='community',
                      cmap='accent',
                      edge_cmap='category20',
                      node_tooltip=['name'],
                      #node_label='name',
                      font_color="black",
                      #font_size='11',
                      width=800,
                      height=600,
                      )

    #chart.configure_view(width=800, height=600,)
    chart.Overlay.opts(title=f"REMP network {start}-{end}")
    if not charts:
        charts = chart
    else:
        charts = charts + chart

# N.B. this is an alternative visualisation

charts.Overlay.opts(title="REMP networks 1950s-1970s")
