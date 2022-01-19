from iso3166 import countries
import altair as alt
import pandas as pd
from .datasets import cat_p_df
from scripts.graphs_and_tables import autlst
from scripts.network_overlap import decade_board_df

c_nrs = cat_p_df.loc[cat_p_df.fullname.isin(autlst)][['fullname','prs_country']].prs_country.value_counts().rename_axis('country').reset_index(name='number')
c_nrs.loc[c_nrs.country=='UK','country'] = 'GB'
c_nrs['numeric'] = c_nrs.country.map(lambda x:int(countries.get(x).numeric))


per_decade_df = {}

canonic_countries = {'prs_country':{'UK':'GB',
                                   'USA': 'US',
                                   'UK /AU': 'AU',
                                   '': 'US', }
                    }
canonic_board_df = decade_board_df.replace(canonic_countries)
canonic_board_df = canonic_board_df.loc[canonic_board_df.prs_country!='unknown']

for decade in range(1950, 2000, 10):
    decade_df = canonic_board_df.loc[canonic_board_df[decade]>0].prs_country.value_counts().rename_axis('country').reset_index(name='number')
    decade_df['numeric']= decade_df.country.map(lambda x:int(countries.get(x).numeric))
    per_decade_df[decade] = decade_df


import altair as alt
from vega_datasets import data

# Data generators for the background
sphere = alt.sphere()
graticule = alt.graticule()

colours_obj = alt.Color('number:Q',
              scale=alt.Scale(scheme='reds'),
              title = "number",
              legend = None)

# Source of land data
source = alt.topo_feature(data.world_110m.url, 'countries')


# Layering and configuring the components
aut_map = alt.layer(
    alt.Chart(sphere).mark_geoshape(fill='white'),
    alt.Chart(graticule).mark_geoshape(stroke='white', strokeWidth=0.5),
    alt.Chart(source
             ).mark_geoshape(stroke='black',).encode(
                                color=colours_obj
                            ).transform_lookup(
                                lookup='id',
                                from_=alt.LookupData(c_nrs, key='numeric', fields=['number']))
).project(
    'mercator',
    scale=100,
    center= [-80,70]
).properties(width=400, height=700)


histogram = alt.Chart(c_nrs).mark_bar().encode(
    x='country',
    y=alt.Y('number:Q'),
    color='number:Q'
).properties(
    height=400,
    width=100
)

compound_aut_chart = alt.hconcat(
    aut_map,
    histogram
).configure_view(stroke=None)

# ========================
# map people from boards
# ========================

board_charts = alt.hconcat()

for decade in per_decade_df:
    dec_colours_obj = alt.Color('number:Q',
                            scale=alt.Scale(scheme='blues'),
                            title="number",
                            legend=None)
    board_map = alt.layer(
        alt.Chart(sphere, title=f"{decade}").mark_geoshape(fill='white'),
        alt.Chart(graticule).mark_geoshape(stroke='white', strokeWidth=0.5),
        alt.Chart(source
                 ).mark_geoshape(stroke='black',).encode(
                                    color=dec_colours_obj
                                ).transform_lookup(
                                    lookup='id',
                                    from_=alt.LookupData(per_decade_df[decade], key='numeric', fields=['number']))
    ).project(
        'mercator',
        scale=100,
        center= [-135,85]
    ).properties(width=500, height=400)


    histogram = alt.Chart(per_decade_df[decade]).mark_bar().encode(
        x='country',
        y=alt.Y('number:Q'),
        color='number:Q'
                    ).properties(
        height=400,
        width=100
    )

    compound_chart = alt.hconcat(
        board_map,
        histogram
    )

    board_charts &= compound_chart

board_charts.configure_axis(
        labelFontSize=9, titleFontSize=16
                    ).configure_view(stroke=None)