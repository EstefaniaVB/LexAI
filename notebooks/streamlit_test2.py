import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import math



######streamlit part#####



st.title('Twitter User locations')

#map_tweets = pd.read_csv('region_count.csv')

map_tweets_loc = pd.read_csv('country_counts.csv')


###pydeck with our data ###

tooltip = {
    "html":
        "<b>Country:</b> {country} <br/>"
        "<b>Tweets:</b> {tweets} <br/>"
        "<b>Retweets:</b> {retweets} <br/>"
        "<b>Likes:</b> {likes} <br/>"
        "<b>Sentiment (per tweet):</b> {sent_ref} <br/>",
    
    "style": {
        "backgroundColor": "white",
        "color": "grey",
    }
}

st.pydeck_chart(pdk.Deck(
map_style='mapbox://styles/mapbox/light-v9',
tooltip=tooltip,
initial_view_state=pdk.ViewState(
    latitude=52.520,
    longitude=-13.404,
    zoom=5,
    pitch=50,
),
layers = [pdk.Layer(
          'ScatterplotLayer',
          data=map_tweets_loc,
          pickable=True,
          get_position='[lon, lat]',
          get_color=['r', 'g', 'b', 's'],
          get_radius= 'radius',
      ),
    ],
))