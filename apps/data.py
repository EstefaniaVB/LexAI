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
import altair as alt
from wordcloud import WordCloud, STOPWORDS
import math
import altair as alt
import numpy as np
import pandas as pd


def app():
    st.title('Regulations')
    #Page style
    st.markdown(
        '<style>h2{color: #731F7D;font-family: Arial, Helvetica, sans-serif;} </style>',
        unsafe_allow_html=True)

    c1, c2 = st.beta_columns([2, 2])  #search bar and hist
    c3, c4 = st.beta_columns([2, 2])  #search bar and hist



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

    # Graph volume regulations
    with c2:
        params = dict(q=query, limit=100000)
        lexai_url = "http://35.223.18.2/indexes/eurlex/search"
        result = requests.get(lexai_url, params=params, headers=headers).json()
        data_eurlex_df = pd.DataFrame(result["hits"])

        data_eurlex_df['year/month'] = data_eurlex_df['date'].str[0:7]

        source = data_eurlex_df
        chart = alt.Chart(source).mark_bar().encode(
            alt.X('year/month', title='Year / Month'),
            alt.Y('count(year/month)', title='Number of laws')).properties(
                width=600).configure_axis(grid=False)
        st.write(chart)


    #Regulation Box

    with c3:
        '''
        ## Regulations
        '''
        ## Range selector
        today = date.today()
        initial_value_for_start_date = today + relativedelta(months=-12)
        initial_value_for_end_date = today
        start_date, end_date = st.date_input(
            "Filter regulations by date: ",
            [initial_value_for_start_date, initial_value_for_end_date])
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        regulation = get_regulation()
        expander = st.beta_expander("expand")
        with expander:
            for i in regulation:
                if i["date"] >= start_date and i["date"] <= end_date:
                    st.write('Title: ', i["title"])
                    st.write('Author: ', i["author"])
                    st.write('Date: ', i["date"])
                    st.write('Link: ', i["link"])

    #Deadlines Box
    with c4:
        '''
        ## Consultations
        '''
        ## Range selector

        #today = date.today()
        #initial_value_for_start_date = today + relativedelta(months=-12)
        #initial_value_for_end_date = today
        #start_date, end_date = st.date_input("Filter consultations by date: ", [initial_value_for_start_date,initial_value_for_end_date])
        #start_date = pd.to_datetime(start_date).date()
        #end_date = pd.to_datetime(end_date).date()
        consultation = get_consultations()
        expander1 = st.beta_expander("expand")
        expander2 = st.beta_expander("expand")

        with expander1:
            checkbox_val_1 = st.checkbox("Open")
            checkbox_val_2 = st.checkbox("Closed")
            checkbox_val_3 = st.checkbox("Upcoming")
            checkbox_val_4 = st.checkbox("Disabled")
            checkbox_val_5 = st.checkbox("Other")

        with expander2:
            for i in consultation:
                if checkbox_val_1:
                    if i["status"] == "OPEN":
                        st.write('Title: ', i["title"])
                        st.write('Status: ', i["status"])
                        st.write('Topic: ', i["topics"])
                        st.write('Type of act: ', i["type_of_act"])
                        st.write('End date: ', i["end_date"])
                        st.write('Link: ', i["link"])
                if checkbox_val_2:
                    if i["status"] == "CLOSED":
                        st.write('Title: ', i["title"])
                        st.write('Status: ', i["status"])
                        st.write('Topic: ', i["topics"])
                        st.write('Type of act: ', i["type_of_act"])
                        st.write('End date: ', i["end_date"])
                        st.write('Link: ', i["link"])
                if checkbox_val_3:
                    if i["status"] == "UPCOMING":
                        st.write('Title: ', i["title"])
                        st.write('Status: ', i["status"])
                        st.write('Topic: ', i["topics"])
                        st.write('Type of act: ', i["type_of_act"])
                        st.write('End date: ', i["end_date"])
                        st.write('Link: ', i["link"])
                if checkbox_val_4:
                    if i["status"] == "DISABLE":
                        st.write('Title: ', i["title"])
                        st.write('Status: ', i["status"])
                        st.write('Topic: ', i["topics"])
                        st.write('Type of act: ', i["type_of_act"])
                        st.write('End date: ', i["end_date"])
                        st.write('Link: ', i["link"])
                if checkbox_val_5:
                    if i["status"] == "OTHER":
                        st.write('Title: ', i["title"])
                        st.write('Status: ', i["status"])
                        st.write('Topic: ', i["topics"])
                        st.write('Type of act: ', i["type_of_act"])
                        st.write('End date: ', i["end_date"])
                        st.write('Link: ', i["link"])
                else:
                    print("Click something")
