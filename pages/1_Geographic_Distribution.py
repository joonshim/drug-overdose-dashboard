import streamlit as st
import altair as alt
import numpy as np
import json
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import time
from PIL import Image
from urllib.request import urlopen

#####################################################################

st.set_page_config(layout='wide', page_title='CDC - Drug Overdose Report', page_icon=':pill:')

# Load geojson
with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
    states = json.load(response)

# Load data
@st.cache
def load_data():
    data = pd.read_csv('./data/dod_by_state.csv', dtype={'fips': str})
    data.loc[0:6,'fips'] = ['01','02','04','05','06','08','09']
    return data
data = load_data()

def load_data_sub(data, year):
    filter_col = [col for col in data if col=='location' or col.endswith(f'{year}')]
    data_sub = data[filter_col]
    return data_sub

col_dict = {
    'location':'Location',
    'code':'Code',
    'fips':'FIPS Code',
    'range_category':'Range Categories (Age-adjusted Rate)',
    'rate': "Age-adjusted Rate",
    'num': 'Annual count',
    'rate_2020': 'Age-adjusted Rate',
    'num_2020': 'Annual Count',
    'rate_2019': 'Age-adjusted Rate',
    'num_2019': 'Annual Count',
    'rate_2018': 'Age-adjusted Rate',
    'num_2018': 'Annual Count',
    'rate_2017': 'Age-adjusted Rate',
    'num_2017': 'Annual Count',
    'rate_2016': 'Age-adjusted Rate',
    'num_2016': 'Annual Count'
}

with st.sidebar:
# Sidebar, load datas
#year = st.sidebar.radio('Select count or rate:', ('2016','2017','2018','2019','2020'))
    year = st.radio('Select year:', ('2016','2017','2018','2019','2020'))
    key = st.radio("Select count or rate:", ('num', 'rate'), format_func=col_dict.get, horizontal=True)

if key=='num':
    st.subheader(f'Number of overdose deaths in the Unites States by jurisdiction in {year}')
if key=='rate':
    st.subheader(f'Age-adjusted rate of overdose deaths in the United States by jurisdiction in {year}')

# Sub dataframe for bar chart
data_sub = load_data_sub(data,year).copy()
data_sub.loc[len(data_sub)] = ['Overall',round(np.mean(data_sub.iloc[:,1]),2),round(np.mean(data_sub.iloc[:,2]),2)]

# Choropleth plot
fig1 = px.choropleth_mapbox(data,
                           geojson=states,
                           locations='fips',
                           color=f'{key}_{year}',
                           color_continuous_scale="dense",
                           zoom=2.3,
                           hover_name='location',
                           hover_data={'fips':False, f'num_{year}':True, f'rate_{year}':True},
                           labels={f'num_{year}':'Annual Count  (#)', f'rate_{year}':'Age-adjusted rate'}
)
fig1.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=2.5,
    mapbox_center={"lat": 40.8902, "lon": -98.8129},
    width=1100,
    height=600
)
st.write(fig1)

# Bar chart
fig2 = alt.Chart(data_sub).mark_bar().encode(
    x=alt.X('location:O',title='State',sort=alt.EncodingSortField(field=f'{key}_{year}',op='sum',order='descending')),
    y=alt.Y(f'{key}_{year}:Q',title=col_dict[f'{key}_{year}']),
    # x=alt.X(f'{key}_{year}:Q',title=col_dict[f'{key}_{year}']),
    # y=alt.Y('location:O',title='State',
    #         sort=alt.EncodingSortField(field=f'{key}_{year}',op='sum',order='descending')),
    color=alt.condition(
        alt.datum.location=='Overall',
        alt.value('orange'),
        alt.value('steelblue')
    )
).properties(width=940, height=500)

# text = fig2.mark_text(
#     align='left',
#     baseline='middle',
#     dx=-10,
#     dy=-10  # Nudges text so it doesn't appear on top of the bar
# ).encode(
#     text=f'{key}_{year}:Q'
# )

st.altair_chart(fig2)
# st.altair_chart(fig2+text)