import streamlit as st
import io
from typing import List, Optional
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

st.set_page_config(layout="wide",initial_sidebar_state="expanded")

query = st.text_input("Search for a topic", 'Eg: Technology')
c1, c2, c3, c4 = st.beta_columns((1, 1, 1, 1))

lexai_eurlex_url = "http://127.0.0.1:8000/query"
tweet_params=dict(query=query,n=5)
eurlex = requests.get(lexai_eurlex_url,params=tweet_params).json()

def get_regulation():
    reg = []
    for i in eurlex:
        #It would be nice to have a list and small text
        #reg.append(st.write(eurlex[i]['title']))
        reg.append(st.write(eurlex[i]['author']))
        reg.append(st.write(eurlex[i]['date']))
        reg.append(st.write(eurlex[i]['link']))
    return reg


def get_consultations():
    lexai_eurlex_url = "http://127.0.0.1:8000/query"
    consults_params=dict(query=query,index='consultations',n=50)
    consults = requests.get(lexai_eurlex_url,params=consults_params).json()
    consultations = []
    for i in consults:
        consultations.append(st.write('Title: ',consults[i]['title']))
        consultations.append(st.write('Type of act: ',consults[i]['type_of_act']))
        #consultations.append(st.write('Start date: ',consults[i]['start_date']))
        consultations.append(st.write('End date: ',consults[i]['end_date']))
        consultations.append(st.write('Link: ',consults[i]['link']))
    return consultations

#Regulation Box

with c1:
    
    '''
    ## REGULATIONS
    '''
    ## Range selector
    d3 = st.date_input("Filter regulations by date:", [])
    regulation = get_regulation()
    
#Deadlines Box
with c2:
    
    '''
    ## CONSULTATIONS
    '''
    ## Range selector
    d4 = st.date_input("Filter consultations by date:", [])
    st.write("Search by type of regulation:")
    checkbox_val = st.checkbox("Open")
    checkbox_val = st.checkbox("Closed")
    expander=st.beta_expander("expand")
    with expander:
        consultation = get_consultations()

with c3:
    '''
    ## Twitter says nothing
    '''

# API QUERIES
#indices=['eurlex', 'consultations', 'twitter_query', 'twitter_press', 'twitter_politicians'])


## TWITTER
#lexai_twitter_url = "http://127.0.0.1:8000/predict"
#tweet_params=dict(keyword=query)
#tweet_likes = requests.get(lexai_twitter_url,params=tweet_params).json()


#st.write('Tweets about this topic were liked by',tweet_likes[0], 'people on Twitter')

