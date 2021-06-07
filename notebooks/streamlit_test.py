import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import math

st.title('My first app')

cents = pd.read_csv('cents_eur_trunc.csv')
cents = cents[['lat','lon']]
cents = cents.dropna()

map_tweets = pd.read_csv('region_count.csv')

map_tweets_loc = pd.read_csv('map_tweets.csv')


map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)

st.map(cents)

# st.map(map_tweets)

chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)

####pydeck test####

df = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.pydeck_chart(pdk.Deck(
map_style='mapbox://styles/mapbox/light-v9',
initial_view_state=pdk.ViewState(
    latitude=37.76,
    longitude=-122.4,
    zoom=11,
    pitch=50,
),
layers=[
    pdk.Layer(
       'HexagonLayer',
       data=df,
        get_position='[lon, lat]',
         radius=200,
          elevation_scale=4,
         elevation_range=[0, 1000],
          pickable=True,
        extruded=True,
     ),
      pdk.Layer(
           'ScatterplotLayer',
           data=df,
         get_position='[lon, lat]',
          get_color='[200, 30, 0, 160]',
          get_radius=200,
      ),
    ],
))
###pydeck test 2###

df = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.pydeck_chart(pdk.Deck(
map_style='mapbox://styles/mapbox/light-v9',
initial_view_state=pdk.ViewState(
    latitude=37.76,
    longitude=-122.4,
    zoom=11,
    pitch=50,
),
layers=[
    pdk.Layer(
       'HexagonLayer',
       data=df,
        get_position='[lon, lat]',
         radius=200,
          elevation_scale=4,
         elevation_range=[0, 1000],
          pickable=True,
        extruded=True,
     )
    ],
))

###pydeck with our data ###



st.pydeck_chart(pdk.Deck(
map_style='mapbox://styles/mapbox/light-v9',
initial_view_state=pdk.ViewState(
    latitude=52.520,
    longitude=-13.404,
    zoom=5,
    pitch=50,
),
layers = [pdk.Layer(
           'ScatterplotLayer',
           data=map_tweets_loc,
         get_position='[lon, lat]',
          get_color='[200, 30, 0, 160]',
          get_radius= 'radius',
      ),
    ],
))