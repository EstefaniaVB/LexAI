import requests
import datetime
from dateutil.relativedelta import relativedelta  # to add days or years
from datetime import date
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

def app():


#    c1, c2 = st.beta_columns([2, 2])  #search bar and hist

#Page style

    st.markdown(
        '<style>h1{color: #731F7D;font-family: Arial, Helvetica, sans-serif;} </style>',
        unsafe_allow_html=True)
    st.markdown(
        '<style>h3{color: #6082FD;font-family: Arial, Helvetica, sans-serif;font_size:1} </style>',
        unsafe_allow_html=True)

    #INPUT SEARCH BAR
    #with c1:
    query = st.text_input("Search for a topic", 'Technology')
    st.markdown('<i class="material-icons"></i>', unsafe_allow_html=True)
    

    # Loadind todays date for Regulation calendar
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

    ### FEATURES ###

    # Graph volume regulations
    #with c3:
    st.title("Volume of regulations")

    params = dict(q=query, limit=100000)
    lexai_url = "http://35.223.18.2/indexes/eurlex/search"
    result = requests.get(lexai_url, params=params, headers=headers).json()
    data_eurlex_df = pd.DataFrame(result["hits"])
    data_eurlex_df['year/month'] = data_eurlex_df['date'].str[0:7]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=data_eurlex_df['year/month'],
    #    xbins=dict(start='2019-01-01', end='2021-06-01', size= 'M1'), # 1 month, 
    #        autobinx = False,
    #        name='control',  # name used in legend and hover labels,
        marker_color='#6082FD',
        opacity=0.90,
        xbins_size=1
    ))
    fig.update_layout(
    #    xaxis_type='date',
        xaxis_title_text='Month', # xaxis label
        xaxis_title_font_family='Helvetica',
        xaxis_title_font_color='#731F7D',
        xaxis_tickfont_family='Helvetica',
        xaxis_tickfont_color='#731F7D',
        xaxis_categoryorder='category ascending',
        yaxis_title_text='Number of regulations', # yaxis label
        yaxis_title_font_family='Helvetica',
        yaxis_title_font_color='#731F7D',
        yaxis_tickfont_family='Helvetica',
        yaxis_tickfont_color='#731F7D',
        yaxis_showgrid=True,
        bargap=0.1, # gap between bars of adjacent location coordinates
        autosize=False,
        width=1600,
        height=500,
        plot_bgcolor='rgba(96, 130, 253,0.06)',
    )
    st.plotly_chart(fig)

    c2, c4 = st.beta_columns([2, 2])  #search bar and hist

#Regulation Box

    with c2:
        '''
        ## Regulations
        '''
        st.title('Regulations')
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
                    st.markdown(f'**Title:  **{i["title"]}',
        unsafe_allow_html=True)
                    st.markdown(f'**Author:  **{i["author"]}',
        unsafe_allow_html=True)
                    st.markdown(f'**Date:  **{i["date"]}',
        unsafe_allow_html=True)
                    st.markdown(f'**Link:  **{i["link"]}',
        unsafe_allow_html=True)
                    st.write("----------------------")

    #Deadlines Box
    with c4:
        '''
        ## Consultations
        '''
        st.title("Consultations")

        checkbox_val_1 = st.checkbox("Open")
        checkbox_val_2 = st.checkbox("Closed")
        checkbox_val_3 = st.checkbox("Upcoming")
        checkbox_val_4 = st.checkbox("Disabled")
        checkbox_val_5 = st.checkbox("Other")
        
        consultation = get_consultations()
        
        expander2 = st.beta_expander("expand")
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
