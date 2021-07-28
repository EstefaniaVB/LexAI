from matplotlib import pyplot as plt
from matplotlib import colors 
import streamlit.components.v1 as components
import requests
import matplotlib.pyplot as plt
import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta  # to add days or years
import pydeck as pdk
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
import functions as fc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def app():
    st.markdown(
        '<style>h1{color: #731F7D;font-family: Arial, Helvetica, sans-serif;} </style>',
        unsafe_allow_html=True)

    st.title("Sorry, this page is under construction ⚙️")
    '''
        ## Sorry, this page is under construction ⚙️
        '''