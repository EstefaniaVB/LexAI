from typing import List, Optional
from altair.vegalite.v4.schema.core import Month
import streamlit.components.v1 as components
import requests
import matplotlib.pyplot as plt
import streamlit as st
from plotly.subplots import make_subplots
import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta  # to add days or years
from datetime import date
import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
import requests
#import altair as alt
from wordcloud import WordCloud, STOPWORDS
#import math
#import altair as alt
#import numpy as np
import pandas as pd
#import math
from geopy import geocoders
from geopy.geocoders import Nominatim
import requests
import functions as fc

def app():
    st.title('Opinions')

    #Page style
    st.markdown(
        '<style>h2{color: #731F7D;font-family: Arial, Helvetica, sans-serif;} </style>',
        unsafe_allow_html=True)


    c1, c6 = st.beta_columns([2, 2])  #search bar and hist
    c4, c5 = st.beta_columns([2, 2])  #search bar and hist
    c2, c3= st.beta_columns([2, 2])  #search bar and hist
    #c7 = st.beta_columns([4])


    #INPUT SEARCH BAR
    with c1:
        #components.html('<div style="position: relative; width: 100%; height: 0; padding-top: 100.0000%; padding-bottom: 48px; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden; border-radius: 8px; will-change: transform;">  <iframe style="position: absolute; width: 100%; height: 50%; top: 0; left: 0; border: none; padding: 0;margin: 0;"    src="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAEfatHdF58&#x2F;view?embed">  </iframe></div><a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAEfatHdF58&#x2F;view?utm_content=DAEfatHdF58&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">LexAI</a> de Estefanía Vidal Bouzón')
        st.image('Images/LexAI2.png', width=200)
        '''
        ## Navigating public fora
        '''
        query = st.text_input("Search for a topic", 'Technology')
        st.markdown('<i class="material-icons"></i>', unsafe_allow_html=True)

    # ??
    today = datetime.datetime.now()
    limit_date = today + relativedelta(days=-7)
    today_time = today.timestamp()
    limit_time = limit_date.timestamp()

    #params
    params = dict(q=query)
    tweet_params = dict(q=query,
                        filters=f"timestamp > {limit_time}",
                        limit=20000)
    tweet_params_without_query = dict(q="",
                                      filters=f"timestamp > {limit_time}")

    headers = {'X-Meili-API-Key': 'OTkwNzQ0ZGRkZTc0NDcwM2RlMzFlOGIx'}

    #Data from News
    lexai_url_news = "http://35.223.18.2/indexes/twitter_press/search"
    news = requests.get(lexai_url_news, params=tweet_params,
                        headers=headers).json()

    #Data from Politicians
    lexai_url_politicians = "http://35.223.18.2/indexes/twitter_politicians/search"
    politicians = requests.get(lexai_url_politicians,
                               params=tweet_params,
                               headers=headers).json()

    #Data from General
    lexai_url_general = f"http://35.223.18.2/indexes/twitter_query/search/"
    full_data_general = requests.get(lexai_url_general,
                                     params=tweet_params_without_query,
                                     headers=headers).json()
    query_data_general = requests.get(lexai_url_general,
                                      params=tweet_params,
                                      headers=headers).json()

    def get_regulation():
        lexai_url = "http://35.223.18.2/indexes/eurlex/search"
        result = requests.get(lexai_url, params=params, headers=headers).json()
        reg = []
        for i in result["hits"]:
            title = i["title"]
            author = i['author']
            date = pd.to_datetime(i['date']).date()
            link = i['link']
            reg.append({
                "title": title,
                "author": author,
                "date": date,
                "link": link
            })

        return reg

    def get_consultations():
        lexai_url = "http://35.223.18.2/indexes/consultations/search"
        result = requests.get(lexai_url, params=params, headers=headers).json()
        consultations = []
        for i in result["hits"]:
            title = i['title']
            topics = i['topics']
            type_of_act = i['type_of_act']
            status = i["status"]
            try:
                end_date = pd.to_datetime(i['end_date']).date()
            except:
                end_date = pd.to_datetime(i['end_date'])
            link = i['link']
            consultations.append({
                "title": title,
                "status": status,
                "topics": topics,
                "type_of_act": type_of_act,
                "end_date": end_date,
                "link": link
            })

        return consultations

    def get_news():
        lexai_url = "http://35.223.18.2/indexes/twitter_press/search"
        result = requests.get(lexai_url, params=params, headers=headers).json()
        info = []
        for i in result["hits"]:
            link = i["link"]
            if i["text_en"]:
                text = i["text_en"]
            else:
                text = i["text"]
            user = i["user"]
            date = i["date"]
            html_link = f'<blockquote data-cards="hidden" class="twitter-tweet" data-height="10%" data-width="100%"> <p lang="en" dir="ltr">{text}.<a href={link}</a></p>&mdash; {user} (@{user}) <a href={link}>{date}</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
            info.append({
                "link": link,
                "text": text,
                "user": user,
                "date": date,
                "html_link": html_link
            })
        return pd.DataFrame(info).sort_values(by="date",
                                              ascending=False).reset_index()

    def get_politicians():
        lexai_url = "http://35.223.18.2/indexes/twitter_politicians/search"
        result = requests.get(lexai_url, params=params, headers=headers).json()
        info = []
        for i in result["hits"]:
            link = i["link"]
            if i["text_en"]:
                text = i["text_en"]
            else:
                text = i["text"]
            user = i["user"]
            date = i["date"]
            html_link = f'<blockquote data-cards="hidden" class="twitter-tweet" data-height="10%" data-width="100%"> <p lang="en" dir="ltr">{text}.<a href={link}</a></p>&mdash; {user} (@{user}) <a href={link}>{date}</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
            info.append({
                "link": link,
                "text": text,
                "user": user,
                "date": date,
                "html_link": html_link
            })
        return pd.DataFrame(info).sort_values(by="date",
                                              ascending=False).reset_index()


    ### FEATURES ###
    #Industry news
    with c2:
        '''
        ## Industry News
        '''
        expander = st.beta_expander("expand")
        with expander:
            html_tweet = get_news()["html_link"]
            list_of_tweets = []
            for e in range(len(html_tweet)):
                list_of_tweets.append(
                    components.html(html_tweet[e], scrolling=True))

    #Politician news
    with c3:
        '''
        ## Politicians News
        '''
        expander = st.beta_expander("expand")
        with expander:
            html_tweet = get_politicians()["html_link"]
            list_of_tweets = []
            for e in range(len(html_tweet)):
                list_of_tweets.append(
                    components.html(html_tweet[e], scrolling=True))

# Sentiment pie-charts
    fig, ax1 = plt.subplots(figsize=(10, 5))
    plt.figure(figsize=(10, 5))

    def label_function(val):
        return f'{val:.0f}%'

    with c4:
        '''
        ## Twitter sentiment
        '''

        fig, ax1 = plt.subplots(figsize=(10, 5))
        plt.figure(figsize=(10, 5))
        data_df = pd.DataFrame(full_data_general['hits'])
        data_df.groupby('sentiment').size().plot(
            kind='pie',
            colors=['tomato', 'lightgrey', '#b5eb9a'],
            autopct=label_function,
            ax=ax1)
        #    ax1.set_ylabel('All tweets', size=22)
        st.write(fig)

    with c5:
        '''
        ## On Topic sentiment
        '''

        fig, ax2 = plt.subplots(figsize=(10, 5))
        plt.figure(figsize=(10, 5))
        topic_df = pd.DataFrame(query_data_general['hits'])

        topic_df.groupby('sentiment').size().plot(
            kind='pie',
            colors=['tomato', 'lightgrey', '#b5eb9a'],
            autopct=label_function,
            ax=ax2)
        #    ax2.set_ylabel('On topic', size=22)
        st.write(fig)

    # cloud of words
    with c6:
        '''
        ## Trending topics
        '''
        general_df = pd.DataFrame(query_data_general["hits"])
        news_df = pd.DataFrame(news["hits"])
        politicians_df = pd.DataFrame(politicians["hits"])

        hashtags = []
        for i in general_df['hashtags']:
            if i != '':
                for j in i.lower().split(', '):
                    hashtags.append(j)
        for i in news_df['hashtags']:
            if i != '':
                for j in i.lower().split(', '):
                    hashtags.append(j)
        for i in politicians_df['hashtags']:
            if i != '':
                for j in i.lower().split(', '):
                    hashtags.append(j)

        text = ' '.join(item for item in hashtags)

        # Define a function to plot word cloud
        def plot_cloud(wordcloud):
            # Set figure size
            plt.figure(figsize=(8, 16))
            # Display image
            plt.imshow(wordcloud)
            # No axis details
            plt.axis("off")

        # Import package

        STOPWORDS.add(query)
        # Generate word cloud
        wordcloud = WordCloud(width=800,
                              height=400,
                              random_state=1,
                              background_color='white',
                              colormap='gray',
                              mode='RGB',
                              collocations=False,
                              stopwords=STOPWORDS,
                              max_words=10).generate(text)
        # Plot

        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()


    #with c7:
    ######### all the data part ########
    source = 'twitter_query'     #sources: twitter_query, twitter_politicians, twitter_press

    ####### api retrieve #######

    data_dict = fc.get_tweets(query,source)

    ####### refining the dataframes #######

    if source == 'twitter_query':
        map_data = fc.refine_cities(data_dict)

    else:
        map_data = fc.refine_countries(data_dict)



    ######streamlit part#####


    st.title(f'source: {source}')


    map_tweets_loc = map_data


    ###plotting our tweet-counts on a geographical map ###

    tooltip_country = {     #tooltip shows a chart when the user hovers over the map
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

    tooltip_city = {     #tooltip shows a chart when the user hovers over the map
        "html":
            "<b>City:</b> {city} <br/>"
            "<b>Tweets:</b> {tweets} <br/>"
            "<b>Retweets:</b> {retweets} <br/>"
            "<b>Likes:</b> {likes} <br/>"
            "<b>Sentiment (per tweet):</b> {sent_ref} <br/>",

        "style": {
            "backgroundColor": "white",
            "color": "grey",
        }
    }

    if source == 'twitter_query':
        tooltip = tooltip_city
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
