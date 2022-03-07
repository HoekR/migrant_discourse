import altair as alt
from vega_datasets import data as vega_data

from .datasets import read_person_categories
from scripts.data_wrangling import get_author_country_counts
from scripts.data_wrangling import get_per_decade_administrators


def get_compound_author_chart():
    c_nrs = get_author_country_counts()
    # Data generators for the background
    sphere = alt.sphere()
    graticule = alt.graticule()

    colours_obj = alt.Color('number:Q',
                            scale=alt.Scale(scheme='reds'),
                            title="number",
                            legend=None)

    # Source of land data
    source = alt.topo_feature(vega_data.world_110m.url, 'countries')

    # Layering and configuring the components
    aut_map = alt.layer(
        alt.Chart(sphere).mark_geoshape(fill='white'),
        alt.Chart(graticule).mark_geoshape(stroke='white', strokeWidth=0.5),
        alt.Chart(source
                  ).mark_geoshape(stroke='black', ).encode(
            color=colours_obj
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(c_nrs, key='numeric', fields=['number']))
    ).project(
        'mercator',
        scale=100,
        center=[-80, 70]
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
    return compound_aut_chart

# ========================
# map people from admins
# ========================


def make_admin_chart():
    per_decade_df = get_per_decade_administrators()
    admin_charts = alt.hconcat()
    sphere = alt.sphere()
    graticule = alt.graticule()
    # Source of land data
    source = alt.topo_feature(vega_data.world_110m.url, 'countries')

    for decade in per_decade_df:
        dec_colours_obj = alt.Color('number:Q',
                                    scale=alt.Scale(scheme='blues'),
                                    title="number",
                                    legend=None)
        admin_map = alt.layer(
            alt.Chart(sphere, title=f"{decade}").mark_geoshape(fill='white'),
            alt.Chart(graticule).mark_geoshape(stroke='white', strokeWidth=0.5),
            alt.Chart(source
                      ).mark_geoshape(stroke='black', ).encode(
                color=dec_colours_obj
            ).transform_lookup(
                lookup='id',
                from_=alt.LookupData(per_decade_df[decade], key='numeric', fields=['number']))
        ).project(
            'mercator',
            scale=100,
            center=[-135, 85]
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
            admin_map,
            histogram
        )

        admin_charts &= compound_chart

    admin_charts.configure_axis(
        labelFontSize=9, titleFontSize=16
    ).configure_view(stroke=None)
    return admin_charts
