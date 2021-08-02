import streamlit as st
import pydeck as pdk
import functions as fc
from PIL import Image


######### all the data part ########



option = st.selectbox(
     'Which tweets source do you want?',
     ('twitter_query', 'twitter_politicians', 'twitter_press')
     
     )

if option == 'twitter_query':
    option2 = st.selectbox(
     'Which region-type do you want?',
     ('City', 'Country')
     
     )

query = st.text_input('Input your searchword here:')
source = option     #sources: twitter_query, twitter_politicians, twitter_press

####### api retrieve #######

data_dict = fc.get_tweets(query,source)
  
####### refining the dataframes #######

if source == 'twitter_query':
    if option2 == 'City':
        map_data = fc.refine_cities(data_dict)
    if option2 == 'Country':
        map_data = fc.refine_countries(data_dict)


else:
    map_data = fc.refine_pol_press(data_dict)



######streamlit part#####


st.title(f'source: {source}')


st.write('You selected:', option)


map_tweets_loc = map_data


###plotting our tweet-counts on a geographical map ###

tooltip_country = {     #tooltip shows a chart when the user hovers over the map
    "html":
        "<b>Country:</b> {country} <br/>"
        "<b>Tweets:</b> {tweets} <br/>"
        "<b>Retweets:</b> {retweets} <br/>"
        "<b>Likes:</b> {likes} <br/>"
        "<b>Sentiment (per tweet):</b> {sentiment} <br/>",
    
    "style": {
        "backgroundColor": "white",
        "color": "grey",
    }
}

tooltip_city = {     #tooltip shows a chart when the user hovers over the map
    "html":
        "<b>City:</b> {city} <br/>"
        "<b>Tweets:</b> {tweets} <br/>"
        "<b>Retweets:</b> {retweets} <br/>"
        "<b>Likes:</b> {likes} <br/>"
        "<b>Sentiment score:</b> {sentiment} <br/>",
    
    "style": {
        "backgroundColor": "white",
        "color": "grey",
    }
}


if source == 'twitter_query':
    if option2 == 'City':
        tooltip = tooltip_city
    else:
        tooltip = tooltip_country

else:
    tooltip = tooltip_country

st.pydeck_chart(pdk.Deck(
map_style='mapbox://styles/mapbox/light-v9',
tooltip=tooltip,
initial_view_state=pdk.ViewState(
    latitude=48.19231,
    longitude=16.37136,
    zoom=3,
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

image = Image.open('legend.jpg')

st.image(image, caption='legend')