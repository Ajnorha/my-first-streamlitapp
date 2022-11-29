import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

# load geojson
#with open(r'.\data\raw\georef-switzerland-kanton.geojson') as geojson_CH:
    #geojson = json.load(geojson_CH)

with open('./data/raw/georef-switzerland-kanton.geojson') as geojson_CH:
     geojson = json.load(geojson_CH)

# First some Clean Energy Data Exploration
@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

#nrg_df_raw = load_data(path=r".\data\raw\renewable_power_plants_CH_upd.csv")
nrg_df_raw = load_data(path="./data/raw/renewable_power_plants_CH_upd.csv")
nrg_df = deepcopy(nrg_df_raw)
nrg_by_KT_capacity = nrg_df.groupby(['canton'])['electrical_capacity'].count().reset_index(name='count')

# Add title and header
st.title("An Overview of Clean Energy in Switzerland")
st.header("How do the 26 cantons compare in the capacity of clean energy?")

# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)
if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(data=nrg_df)
    # st.table(data=nrg_df)

# Setting up columns
left_column, middle_column, right_column = st.columns([3, 1, 1])

# Widgets: selectbox
Type_of_Energy = ["All"]+sorted(pd.unique(nrg_df['energy_source_level_2']))
Type_of_Energy = left_column.selectbox("Choose an energy source", Type_of_Energy)

nrg_by_KT = nrg_df[nrg_df['energy_source_level_2']==Type_of_Energy].groupby(['canton'])['electrical_capacity'].count().reset_index(name='count')

# Plot Types of Energy
st.subheader("Capacity by Types of Energy and Canton - choose an energy source for more details")
fig1 = px.choropleth_mapbox(nrg_by_KT, geojson=geojson, color='count', locations='canton',
                                    featureidkey='properties.kan_name')
fig1.update_layout(mapbox_style="carto-positron",
                mapbox_zoom=5, mapbox_center = {"lat": 46.947922, "lon": 7.444608})
fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# Plot Energy Capacity by Canton
st.subheader("Total Energy Capacity by Canton")
nrg_by_KT_capacity = nrg_df.groupby(['canton'])['electrical_capacity'].count().reset_index(name='count')
fig2 = px.choropleth_mapbox(nrg_by_KT_capacity, geojson=geojson, color='count', locations='canton',
                                    featureidkey='properties.kan_name')
fig2.update_layout(mapbox_style="carto-positron",
                mapbox_zoom=5, mapbox_center = {"lat": 46.947922, "lon": 7.444608})
fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Flow control and plotting
if Type_of_Energy == "All":
    #nrg_df_all = nrg_by_KT_capacity
    st.plotly_chart(fig2)
else:
    #nrg_by_KT = nrg_by_KT
    st.plotly_chart(fig1)

#Widgets: radio buttons
show_means = middle_column.radio(
  label='Choose Chart', options=['Bar', 'Pie'])

st.subheader("Total Capacity of Renewables")
renewable = nrg_df.groupby(['energy_source_level_2'])['electrical_capacity'].sum().reset_index()
p_fig = px.bar(renewable, x='energy_source_level_2', y='electrical_capacity', title="Capacity of Renewable Energy Sources in Switzerland",
        labels={'energy_source_level_2': 'Energy Source',
               'electrical_capacity':'Electrical Capacity'})
if show_means == "Bar":
    st.plotly_chart(p_fig)

st.subheader("Distribution of Energy Capacity by Canton, part 2")
p_fig4 = px.pie(nrg_df, values='electrical_capacity',
              names='canton', title='Energy Capacity by Canton', color_discrete_sequence=px.colors.sequential.RdBu, width=800, height=800)
p_fig4.update_traces(textposition='inside')
p_fig4.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
if show_means == "Pie":
    st.plotly_chart(p_fig4)


st.subheader("Locations of Energy Source Capacity in Switzerland by Energy Source")
p_fig3 = px.scatter_mapbox(nrg_df,
                         lat="lat",
                         lon="lon",
                         color="energy_source_level_2",
                         size="electrical_capacity",
                         color_continuous_scale=px.colors.cyclical.IceFire,
                         size_max=20,
                         zoom=6,
                         height=700,
                         hover_name='energy_source_level_2')
p_fig3.update_layout(mapbox_style='open-street-map')
st.plotly_chart(p_fig3)

