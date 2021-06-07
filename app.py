import streamlit as st
import io
from typing import List, Optional
import streamlit.components.v1 as components
import requests
import markdown
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly import express as px
from plotly.subplots import make_subplots
import streamlit as st
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta # to add days or years
from IPython.core.display import display, HTML
from datetime import date


st.set_page_config(layout="wide",initial_sidebar_state="expanded")
st.markdown('<style>h2{color: #731F7D;font-family: Arial, Helvetica, sans-serif;} </style>', unsafe_allow_html=True)



c7, c8, c9 = st.beta_columns((2,1,1))
c1, c2, c5 = st.beta_columns((1,1,2))
c3, c4, c5= st.beta_columns((1,1,2))

with c7:
    #components.html('<div style="position: relative; width: 100%; height: 0; padding-top: 100.0000%; padding-bottom: 48px; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden; border-radius: 8px; will-change: transform;">  <iframe style="position: absolute; width: 100%; height: 50%; top: 0; left: 0; border: none; padding: 0;margin: 0;"    src="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAEfatHdF58&#x2F;view?embed">  </iframe></div><a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAEfatHdF58&#x2F;view?utm_content=DAEfatHdF58&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">LexAI</a> de Estefanía Vidal Bouzón')
    st.image('Images/LexAI2.png', width=200)
    '''
    ## Navigating public fora
    '''
    query = st.text_input("Search for a topic", 'Technology')
    st.markdown('<i class="material-icons"></i>', unsafe_allow_html=True)


params=dict(q=query)
headers={'X-Meili-API-Key':'OTkwNzQ0ZGRkZTc0NDcwM2RlMzFlOGIx'}




def get_regulation():
    lexai_url = "http://35.223.18.2/indexes/eurlex/search"
    result = requests.get(lexai_url,params=params,headers=headers).json()
    reg = []
    for i in result["hits"]:
        title=i["title"]
        author= i['author']
        date= pd.to_datetime(i['date']).date()
        link = i['link']
        reg.append({"title":title,"author":author,"date":date,"link":link})
    
    return reg


def get_consultations():
    lexai_url = "http://35.223.18.2/indexes/consultations/search"
    result = requests.get(lexai_url,params=params,headers=headers).json()
    consultations = []
    for i in result["hits"]:
        title = i['title']
        topics = i['topics']
        type_of_act = i['type_of_act']
        status =  i["status"]
        try:
            end_date = pd.to_datetime(i['end_date']).date()
        except:
            end_date = pd.to_datetime(i['end_date'])
        link = i['link']
        consultations.append({"title":title,"status":status,"topics":topics,"type_of_act":type_of_act,"end_date":end_date,"link":link})

    return consultations

def get_news():
    lexai_url = "http://35.223.18.2/indexes/twitter_press/search"
    result = requests.get(lexai_url,params=params,headers=headers).json()
    info=[]
    for i in result["hits"]:
        link = i["link"]
        text= i["text"]
        user= i["user"]
        date= i["date"]
        html_link = f'<blockquote data-cards="hidden" class="twitter-tweet" data-height="10%" data-width="100%"> <p lang="en" dir="ltr">{text}.<a href={link}</a></p>&mdash; {user} (@{user}) <a href={link}>{date}</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
        info.append({"link":link,"text":text,"user":user,"date":date,"html_link":html_link})
    return pd.DataFrame(info).sort_values(by="date", ascending=False)

def get_politicians():
    lexai_url = "http://35.223.18.2/indexes/twitter_politicians/search"
    result = requests.get(lexai_url,params=params,headers=headers).json()
    info=[]
    for i in result["hits"]:
        link = i["link"]
        text= i["text"]
        user= i["user"]
        date= i["date"]
        html_link = f'<blockquote data-cards="hidden" class="twitter-tweet" data-height="10%" data-width="100%"> <p lang="en" dir="ltr">{text}.<a href={link}</a></p>&mdash; {user} (@{user}) <a href={link}>{date}</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
        info.append({"link":link,"text":text,"user":user,"date":date,"html_link":html_link})
    return pd.DataFrame(info).sort_values(by="date", ascending=False)

#Industry news
with c3:
    '''
    ## Industry News
    '''
    expander=st.beta_expander("expand")
    with expander:
        html_tweet = get_news()["html_link"]
        list_of_tweets = []
        for e in range(len(html_tweet)):
            list_of_tweets.append(components.html(html_tweet[e],scrolling=True))

#Politician news
with c4:
    '''
    ## Politicians News
    '''
    expander=st.beta_expander("expand")
    with expander:
        html_tweet = get_politicians()["html_link"]
        list_of_tweets = []
        for e in range(len(html_tweet)):
            list_of_tweets.append(components.html(html_tweet[e],scrolling=True))


#Regulation Box

with c1:
    
    '''
    ## Regulations
    '''
    ## Range selector
    today = date.today()
    initial_value_for_start_date = today + relativedelta(months=-12)
    initial_value_for_end_date = today
    start_date, end_date = st.date_input("Filter regulations by date: ", [initial_value_for_start_date,initial_value_for_end_date])
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    regulation = get_regulation()
    expander=st.beta_expander("expand")
    with expander:    
        for i in regulation:
            if i["date"] >= start_date and i["date"] <= end_date:
                st.write('Title: ',i["title"])
                st.write('Author: ',i["author"])
                st.write('Date: ',i["date"])
                st.write('Link: ',i["link"])
    
#Deadlines Box
with c2:
    
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
    expander1=st.beta_expander("expand")
    expander2=st.beta_expander("expand")
    
    with expander1:  
        checkbox_val_1 = st.checkbox("Open")
        checkbox_val_2 = st.checkbox("Closed")
        checkbox_val_3 = st.checkbox("Upcoming")
        checkbox_val_4 = st.checkbox("Disabled")
        checkbox_val_5 = st.checkbox("Other")
        
    
    with expander2:    
        for i in consultation:
            #if i["end_date"] and (i["end_date"] >= start_date and i["end_date"] <= end_date):
            if checkbox_val_1:
                if i["status"]=="OPEN":
                    st.write('Title: ',i["title"])
                    st.write('Status: ',i["status"])                
                    st.write('Topic: ',i["topics"])
                    st.write('Type of act: ',i["type_of_act"])
                    st.write('End date: ',i["end_date"])
                    st.write('Link: ',i["link"])
            if checkbox_val_2:
                if i["status"]=="CLOSED":
                    st.write('Title: ',i["title"])
                    st.write('Status: ',i["status"])                
                    st.write('Topic: ',i["topics"])
                    st.write('Type of act: ',i["type_of_act"])
                    st.write('End date: ',i["end_date"])
                    st.write('Link: ',i["link"])
            if checkbox_val_3:
                if i["status"]=="UPCOMING":
                    st.write('Title: ',i["title"])
                    st.write('Status: ',i["status"])                
                    st.write('Topic: ',i["topics"])
                    st.write('Type of act: ',i["type_of_act"])
                    st.write('End date: ',i["end_date"])
                    st.write('Link: ',i["link"])
            if checkbox_val_4:
                if i["status"]=="DISABLE":
                    st.write('Title: ',i["title"])
                    st.write('Status: ',i["status"])                
                    st.write('Topic: ',i["topics"])
                    st.write('Type of act: ',i["type_of_act"])
                    st.write('End date: ',i["end_date"])
                    st.write('Link: ',i["link"])
            if checkbox_val_5:
                if i["status"]=="OTHER":
                    st.write('Title: ',i["title"])
                    st.write('Status: ',i["status"])                
                    st.write('Topic: ',i["topics"])
                    st.write('Type of act: ',i["type_of_act"])
                    st.write('End date: ',i["end_date"])
                    st.write('Link: ',i["link"])
            else:
                print("Click something")


#MAP

import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import math


#map_tweets = pd.read_csv('region_count.csv')

map_tweets_loc = pd.read_csv('raw_data/map_tweets.csv')


###pydeck with our data ###
with c5:
    '''
    ## Twitter User locations'''
    
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
            get_fill_color='[180, 0, 200, 140]',
            get_radius= 'radius',
        ),
        ],
    ))