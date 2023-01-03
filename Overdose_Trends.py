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

# Layout
st.set_page_config(layout='wide', page_title='CDC - Drug Overdose Report', page_icon=':pill:')

# Load geojson, load image
def load_logo():
    logo = Image.open('./images/cdc-logo.png')
    return logo
logo=load_logo()

st.title('CDC Drug Overdose Data Report')

with st.sidebar:
    with st.expander("**Incidence Measures**:"):
        st.write("Annual Count")
        st.caption('''The estimated number of overdose deaths that occurred in a specified year.  
        This information can be helpful for understanding the magnitude of the problem.''')
        st.write("Age-adjusted Rate")
        st.caption('''Minimizes the likelihood that observed differences between groups or across years are due to differences in the distribution of age in the underlying population.  
        The calculation of age-adjusted rates is described here: https://doh.wa.gov/sites/default/files/legacy/Documents/5300/TechnicalNotes.pdf''')

    with st.expander("**Glossary of Drug**:"):
        st.write('Opioids')  
        st.caption('Fentanyl, Heroin, and/or Rx Opioids (common prescription opioids)')
        st.write('Stimulants')  
        st.caption('Meth, and/or Cocaine')

with st.expander('About this dashboard:'):
    st.write('''
    This dashboard shows the information about drug overdose deaths in the U.S..  
    Data source: Centers for Disease Control and Prevention (CDC)
    ''')
    st.image(logo, width=150)
    
# Load data
data_time = pd.read_csv('./data/dod_by_time.csv')
data_time = data_time.set_index('year', drop=True)
data_2021 = pd.read_csv('./data/data_2021.csv')

# 1st row
h1,h2,h3,h4,h5 = st.columns((1,1,1,1,1))

count_21 = data_time.loc[2021,'num_total']
count_20 = data_time.loc[2020,'num_total']
rate_21 = data_time.loc[2021,'rate_total']
rate_20 = data_time.loc[2020,'rate_total']
fentanyl_21 = data_time.loc[2021,'num_synthetic']
fentanyl_20 = data_time.loc[2020,'rate_synthetic']

perc_anyopioid = round(data_time.loc[2021,'num_anyopioid']/data_time.loc[2021,'num_total'],2)
perc_fentanyl =  round(data_time.loc[2021,'num_synthetic']/data_time.loc[2021,'num_total'],2)
perc_heroin =  round(data_time.loc[2021,'num_heroin']/data_time.loc[2021,'num_total'],2)
perc_cocaine =  round(data_time.loc[2021,'num_cocaine']/data_time.loc[2021,'num_total'],2)
perc_methamphetamine =  round(data_time.loc[2021,'num_psychostimulant']/data_time.loc[2021,'num_total'],2)
perc_stimulant = perc_cocaine + perc_methamphetamine
data_drug = pd.DataFrame({'Type':['Any Opioids','Fentanyl', 'Heroin', 'Any Stimulants', 'Cocaine', 'Methaamphetamine'],
                    'Value':[perc_anyopioid, perc_fentanyl, perc_heroin, perc_stimulant, perc_cocaine, perc_methamphetamine]})

h1 = st.write('')
h2.metric(label = 'Annual Count (2021)', value=count_21,
        delta=str(count_21-count_20)+' Compared to 2020',delta_color='inverse')
h3.metric(label = 'Age-adjusted Rate (2021)', value=rate_21,
        delta=str(round(rate_21-rate_20,2))+' Compared to 2020',delta_color='inverse')
h4.metric(label = 'Fentanyl-involved Incidents (2021)', value=fentanyl_21, 
        delta=str(fentanyl_21-fentanyl_20)+' Compared to 2020',delta_color='inverse')
h5 = st.write('')

# 2nd row 
g1, g2 = st.columns((1,1.7))

# Cumulative Counts of Drug Overdose Deaths
fig = px.bar(data_2021, x='month', y='count', template='seaborn', 
            hover_name='month', hover_data={'month':False, 'count':True}, height=300)
fig.update_traces(marker_color='#264653')
fig.update_layout(title_text="Cumulative Counts of Drug Overdose Deaths in 2021", title_x=0,
                margin=dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)

g1.plotly_chart(fig, use_container_width=True)

# Percentages of overdose deaths involving select drugs and drug classes
fig = px.bar(data_drug, x='Type', y='Value', color='Value', range_y = [0,1.0], 
            hover_name='Type', hover_data={'Type':False, 'Value':True}, color_continuous_scale='sunset', height=300)
fig.update(layout_coloraxis_showscale=False)
fig.update_layout(title_text="Percentages of overdose deaths involving select drug classes in 2021", title_x=0,
                margin=dict(l=0,r=10,b=10,t=30),yaxis_title=None, xaxis_title=None)
g2.plotly_chart(fig, use_container_width=True)

# 

data = pd.read_csv('./data/dod_by_time.csv')

g3, g4 = st.columns([2.,0.4])

with g4:
    key = st.radio("Select count or rate:", ('Annual Count', 'Age-adjusted Rate'))
    category = st.radio('Select a category:', ('Total','Opioids','Stimulants'))

key_dict = {'Annual Count':'num',
        'Age-adjusted Rate':'rate',
        'num_heroin':'Heroin',
        'rate_heroin':'Heroin',
        'num_natural':'Rx Opioids',
        'rate_natural':'Rx Opioids',
        'num_synthetic':'Fentanyl',
        'rate_synthetic':'Fentanyl',
        'num_cocaine':'Cocaine',
        'rate_cocaine':'Cocaine',
        'num_psychostimulant':'Methamphetamine',
        'rate_psychostimulant':'Methamphetamine'
        }

with g3:
    if category=='Total':
        fig = px.line(data, x='year', y=f'{key_dict[key]}_total', hover_name='year', 
                hover_data={'year':False, f'{key_dict[key]}_total':True}, markers=True, height=400)
        fig.update_layout(legend=dict(yanchor="top",y=0.90,xanchor="left",x=0.01),
            yaxis_title=f'{key}', xaxis_title='Year')
        fig.update_xaxes(tickmode='array',
                tickvals=np.arange(2001,2022,1))
        st.plotly_chart(fig, use_container_width=True)
    if category=='Opioids':
        fig = px.line(data, x='year', y=[f'{key_dict[key]}_heroin', f'{key_dict[key]}_natural',f'{key_dict[key]}_synthetic'], hover_name='year', 
            hover_data={'variable':False, 'year':False, 'value':True}, markers=True, height=400)
        fig.update_layout(legend_title_text='Opioids', legend=dict(yanchor="top",y=0.90,xanchor="left",x=0.01),
            yaxis_title=f'{key}', xaxis_title='Year')
        fig.for_each_trace(lambda t: t.update(name = key_dict[t.name],
                            legendgroup = key_dict[t.name],
                            hovertemplate = t.hovertemplate.replace(t.name, key_dict[t.name])
                            )
        )
        fig.update_xaxes(tickmode='array',tickvals=np.arange(2001,2022,1))
        st.plotly_chart(fig, use_container_width=True)
    if category=='Stimulants':
        fig = px.line(data, x='year', y=[f'{key_dict[key]}_cocaine', f'{key_dict[key]}_psychostimulant'], hover_name='year', 
            hover_data={'variable':False, 'year':False, 'value':True}, markers=True, height=400)
        fig.update_layout(legend_title_text='Stimulants', legend=dict(yanchor="top",y=0.90,xanchor="left",x=0.01),
            yaxis_title=f'{key}', xaxis_title='Year')
        fig.for_each_trace(lambda t: t.update(name = key_dict[t.name],
                            legendgroup = key_dict[t.name],
                            hovertemplate = t.hovertemplate.replace(t.name, key_dict[t.name])
                            )
        )
        fig.update_xaxes(tickmode='array',tickvals=np.arange(2001,2022,1))
        st.plotly_chart(fig, use_container_width=True)