import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import math

st.title('Twitter User locations')

#map_tweets = pd.read_csv('region_count.csv')

map_tweets_loc = pd.read_csv('city_counts.csv')


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