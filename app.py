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
st.markdown('<style>h1{color: red;}</style>', unsafe_allow_html=True)
'''
    # LexAI
    ## Navigating public fora
    '''


c7, c8, c9 = st.beta_columns((1, 1,2))
c1, c2, c5 = st.beta_columns((1, 1,2))
c3, c4, c6 = st.beta_columns((1, 1, 2))

with c7:
    query = st.text_input("Search for a topic", 'Technology')


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
        try:
            end_date = pd.to_datetime(i['end_date']).date()
        except:
            end_date = pd.to_datetime(i['end_date'])
        link = i['link']
        consultations.append({"title":title,"topics":topics,"type_of_act":type_of_act,"end_date":end_date,"link":link})

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
    
    today = date.today()
    initial_value_for_start_date = today + relativedelta(months=-12)
    initial_value_for_end_date = today
    start_date, end_date = st.date_input("Filter consultations by date: ", [initial_value_for_start_date,initial_value_for_end_date])
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    consultation = get_consultations()
    expander2=st.beta_expander("expand")
    #checkbox_val = st.checkbox("Open")
    #checkbox_val = st.checkbox("Closed")
    with expander2:    
        for i in consultation:
            if i["end_date"] and (i["end_date"] >= start_date and i["end_date"] <= end_date):
                st.write('Title: ',i["title"])
                st.write('Title: ',i["topics"])
                st.write('Type of act: ',i["type_of_act"])
                st.write('End date: ',i["end_date"])
                st.write('Link: ',i["link"])


## Displaying tweets (WE NEED TO SORT THE TWEETS BY LASTEST PUBLISHED)
