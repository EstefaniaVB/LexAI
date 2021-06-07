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
'''
    # LexAI
    ## Navigating public fora
    '''

query = st.text_input("Search for a topic", 'Technology')
c1, c2, c3 = st.beta_columns((1, 1, 2))
c4, c5, c6 = st.beta_columns((1, 1, 2))



params=dict(q=query)
headers={'X-Meili-API-Key':'OTkwNzQ0ZGRkZTc0NDcwM2RlMzFlOGIx'}




def get_regulation():
    lexai_url = "http://35.223.18.2/indexes/eurlex/search"
    result = requests.get(lexai_url,params=params,headers=headers).json()
    reg = []
    for i in result:
        #It would be nice to have a list and small text
        reg.append(st.write(result[i]['title']))
        reg.append(st.write(result[i]['author']))
        reg.append(st.write(pd.to_datetime(result[i]['date']).date()))
        reg.append(st.write(result[i]['link']))
    return reg

def get_regulation2():
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
    for i in result:
        consultations.append(st.write('Title: ',result[i]['title']))
        consultations.append(st.write('Type of act: ',result[i]['type_of_act']))
        #consultations.append(st.write('Start date: ',consults[i]['start_date']))
        consultations.append(st.write('End date: ',result[i]['end_date']))
        consultations.append(st.write('Link: ',result[i]['link']))
    return consultations

def get_news():
    lexai_url = "http://35.223.18.2/indexes/twitter_press/search"
    result = requests.get(lexai_url,params=params,headers=headers).json()
    html_code =[]
    for i in result:
        link = result[i]["link"]
        text= result[i]["text"]
        user= result[i]["user"]
        date= result[i]["date"]
        html_link = f'<blockquote class="twitter-tweet"><p lang="en" dir="ltr">{text}.<a href={link}</a></p>&mdash; {user} (@{user}) <a href={link}>{date}</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
        html_code.append(html_link)
    return html_code

def get_news2():
    lexai_url = "http://35.223.18.2/indexes/twitter_press/search"
    result = requests.get(lexai_url,params=params,headers=headers).json()
    info=[]
    for i in result:
        link = result[i]["link"]
        text= result[i]["text"]
        user= result[i]["user"]
        date= result[i]["date"]
        #html_link = f'<blockquote class="twitter-tweet"><p lang="en" dir="ltr">{text}.<a href={link}</a></p>&mdash; {user} (@{user}) <a href={link}>{date}</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
        html_link = f'<blockquote data-cards="hidden" class="twitter-tweet" data-height="1%" data-width="100%"> <p lang="en" dir="ltr">{text}.<a href={link}</a></p>&mdash; {user} (@{user}) <a href={link}>{date}</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
        info.append({"link":link,"text":text,"user":user,"date":date,"html_link":html_link})
    return pd.DataFrame(info).sort_values(by="date", ascending=False)

#Regulation Box

with c1:
    
    '''
    ## Regulations
    '''
    ## Range selector
    today = date.today()
    initial_value_for_start_date = today - relativedelta(months=-12)
    initial_value_for_end_date = today
    start_date, end_date = st.date_input("Pick a date range", [])
    #start_date, end_date = st.date_input("Pick a date range", [])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    regulation = get_regulation2()
    
 
    
    st.write(regulation[(regulation[0]["date"] > start_date)& (regulation[0]["date"] < end_date)]["title"])
    st.write(regulation[(regulation[0]["date"] > start_date)& (regulation[0]["date"] < end_date)]["author"])
    st.write(regulation[(regulation[0]["date"] > start_date)& (regulation[0]["date"] < end_date)]["date"])
    st.write(regulation[(regulation[0]["date"] > start_date)& (regulation[0]["date"] < end_date)]["link"])
    #d3 = st.date_input("Filter regulations by date:", [])
    

    
#Deadlines Box
with c2:
    
    '''
    ## Consultations
    '''
    ## Range selector
    d4 = st.date_input("Filter consultations by date:", [])
    st.write("Search by type of regulation:")
    checkbox_val = st.checkbox("Open")
    checkbox_val = st.checkbox("Closed")
    expander=st.beta_expander("expand")
    with expander:
        consultation = get_consultations()


## Displaying tweets (WE NEED TO SORT THE TWEETS BY LASTEST PUBLISHED)
with c3:
    '''
    ## Industry News
    '''
    expander=st.beta_expander("expand")
    with expander:
        html_tweet = get_news2()["html_link"]
        list_of_tweets = []
        for e in range(len(html_tweet)):
            list_of_tweets.append(components.html(html_tweet[e],scrolling=True,width=500,height=200))

