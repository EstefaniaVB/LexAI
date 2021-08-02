import requests
import datetime
from dateutil.relativedelta import relativedelta  # to add days or years
from datetime import date
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from bokeh.models.widgets import Div


def app():
    #Page style
    st.markdown(
        '<style>h1{color: #731F7D;font-family: Arial, Helvetica, sans-serif;} </style>',
        unsafe_allow_html=True)



    # columns
    c1, c2 = st.beta_columns([1, 3])  #search bar and hist
    c3, c4 = st.beta_columns([2, 2])  #search bar and hist



    with c1:
        #INPUT SEARCH BAR
        query = st.text_input("Search for a topic", 'Technology')
        st.markdown('<i class="material-icons"></i>', unsafe_allow_html=True)
        html_intro='<p><strong><span style="font-family: Helvetica; color: rgb(115, 31, 125);">LexAI, Y</span></strong><strong><span style="font-family: Helvetica; color: rgb(115, 31, 125);">our compass for navigating public fora <span style="color: rgb(115, 31, 125); font-family: Helvetica; font-size: medium; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: justify; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial; display: inline !important; float: none;">🧭</span></span></strong></p>\
            <p style="line-height: 1.5; text-align: justify;"><span style="color: rgb(115, 31, 125);"><span style="font-family: Helvetica;">LexAI helps you keep track of EU <span style="color: rgb(115, 31, 125); font-family: Helvetica; font-size: medium; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: justify; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial; display: inline !important; float: none;">🇪🇺&nbsp;</span>regulations &nbsp;and political, media, and social media attention on any given topic.</span></span></p>\
                <p style="line-height: 1.5; text-align: justify;"><span style="color: rgb(115, 31, 125);"><span style="font-family: Helvetica;">Enter a keyword in the search bar to see the latest regulations on your topic of interest 🤔.</span></span></p>\
                    <p style="line-height: 1.5; text-align: justify;"><span style="color: rgb(115, 31, 125);"><span style="font-family: Helvetica;">Follow the links for more details 🔍️ as well as to give your opinion on future regulations thanks to our consultations feature.</span></span></p>\
                        <p style="line-height: 1.5; text-align: justify;"><span style="color: rgb(115, 31, 125);"><span style="font-family: Helvetica;">Thank you for your visit! 😊</span></span></p>\
                            <p><br></p>'
        st.markdown(html_intro, unsafe_allow_html=True)



    # Loadind todays date for Regulation calendar
    today = datetime.datetime.now()
    limit_date = today + relativedelta(days=-7)
    today_time = today.timestamp()
    limit_time = limit_date.timestamp()

    #params
    params = dict(q=query)
    tweet_params = dict(q=query,
                        filters=f"timestamp > {limit_time}",
                        limit=10000)
    tweet_params_without_query = dict(q="",
                                      filters=f"timestamp > {limit_time}")

    headers = {'X-Meili-API-Key': 'OTkwNzQ0ZGRkZTc0NDcwM2RlMzFlOGIx'}

    #Data from News
    lexai_url_news = "http://127.0.0.1:7700/indexes/twitter_press/search"
    news = requests.get(lexai_url_news, params=tweet_params,
                        headers=headers).json()

    #Data from Politicians
    lexai_url_politicians = "http://127.0.0.1:7700/indexes/twitter_politicians/search"
    politicians = requests.get(lexai_url_politicians,
                               params=tweet_params,
                               headers=headers).json()

    #Data from General
    lexai_url_general = f"http://127.0.0.1:7700/indexes/twitter_query/search/"
    query_data_general = requests.get(lexai_url_general,
                                      params=tweet_params,
                                      headers=headers).json()

    def get_regulation():
        lexai_url = "http://127.0.0.1:7700/indexes/eurlex/search"
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
        lexai_url = "http://127.0.0.1:7700/indexes/consultations/search"
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
    with c2:
        params = dict(q=query, limit=100000)
        lexai_url = "http://127.0.0.1:7700/indexes/eurlex/search"
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
            width=1000,
            height=500,
            plot_bgcolor='rgba(96, 130, 253,0.06)',
        )
        st.plotly_chart(fig)


    #Regulation Box

    with c3:
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
                    st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Title: </span></strong>{i["title"]}</p>',unsafe_allow_html=True)
                    st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253;">Author: </span></strong>{i["author"]}</p>',unsafe_allow_html=True)
                    st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Date: </span></strong>{i["date"]}</p>',unsafe_allow_html=True)
                    if st.button('Link'):
                        js = f"window.open('{i['link']}')"
                        html = '<img src onerror="{}">'.format(js)
                        div = Div(text=html)
                        st.bokeh_chart(div)
                    st.write('-----')

    #Deadlines Box
    with c4:
        '''
        ## Consultations
        '''
        st.title("Consultations")

        checkbox_val_1 = st.checkbox("Open", value=True)
        checkbox_val_2 = st.checkbox("Upcoming", value=True)
        checkbox_val_3 = st.checkbox("Closed")
        checkbox_val_4 = st.checkbox("Disabled")
        checkbox_val_5 = st.checkbox("Other")

        consultation = get_consultations()

        expander2 = st.beta_expander("expand")
        with expander2:
            for i in consultation:
                if checkbox_val_1:
                    if i["status"] == "OPEN":
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Title: </span></strong>{i["title"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Status: </span></strong>{i["status"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Topic: </span></strong>{i["topics"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Type of act: </span></strong>{i["type_of_act"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">End date: </span></strong>{i["end_date"]}</p>',unsafe_allow_html=True)
                        if st.button('Link'):
                            js = f"window.open('{i['link']}')"
                            html = '<img src onerror="{}">'.format(js)
                            div = Div(text=html)
                            st.bokeh_chart(div)
                        st.write('-----')
                if checkbox_val_2:
                    if i["status"] == "UPCOMING":
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Title: </span></strong>{i["title"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Status: </span></strong>{i["status"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Topic: </span></strong>{i["topics"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Type of act: </span></strong>{i["type_of_act"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">End date: </span></strong>{i["end_date"]}</p>',unsafe_allow_html=True)
                        if st.button('Link'):
                            js = f"window.open('{i['link']}')"
                            html = '<img src onerror="{}">'.format(js)
                            div = Div(text=html)
                            st.bokeh_chart(div)
                        st.write('-----')
                if checkbox_val_3:
                    if i["status"] == "CLOSED":
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Title: </span></strong>{i["title"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Status: </span></strong>{i["status"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Topic: </span></strong>{i["topics"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Type of act: </span></strong>{i["type_of_act"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">End date: </span></strong>{i["end_date"]}</p>',unsafe_allow_html=True)
                        if st.button('Link'):
                            js = f"window.open('{i['link']}')"
                            html = '<img src onerror="{}">'.format(js)
                            div = Div(text=html)
                            st.bokeh_chart(div)
                        st.write('-----')
                if checkbox_val_4:
                    if i["status"] == "DISABLE":
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Title: </span></strong>{i["title"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Status: </span></strong>{i["status"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Topic: </span></strong>{i["topics"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Type of act: </span></strong>{i["type_of_act"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">End date: </span></strong>{i["end_date"]}</p>',unsafe_allow_html=True)
                        if st.button('Link'):
                            js = f"window.open('{i['link']}')"
                            html = '<img src onerror="{}">'.format(js)
                            div = Div(text=html)
                            st.bokeh_chart(div)
                        st.write('-----')
                if checkbox_val_5:
                    if i["status"] == "OTHER":
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Title: </span></strong>{i["title"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Status: </span></strong>{i["status"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Topic: </span></strong>{i["topics"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">Type of act: </span></strong>{i["type_of_act"]}</p>',unsafe_allow_html=True)
                        st.markdown(f'<p><strong><span style="color: rgb(96, 130, 253);">End date: </span></strong>{i["end_date"]}</p>',unsafe_allow_html=True)
                        if st.button('Link'):
                            js = f"window.open('{i['link']}')"
                            html = '<img src onerror="{}">'.format(js)
                            div = Div(text=html)
                            st.bokeh_chart(div)
                        st.write('-----')
                else:
                    print("Click something")