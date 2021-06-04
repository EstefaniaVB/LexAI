import streamlit as st
'''
# LexAI Website !!!
It's beautiful
'''


# API QUERIES
query = st.text_input("Search for a topic", 'agriculture')

import requests

#indices=['eurlex', 'consultations', 'twitter_query', 'twitter_press', 'twitter_politicians'])


## TWITTER
#lexai_twitter_url = "http://127.0.0.1:8000/predict"
#tweet_params=dict(keyword=query)
#tweet_likes = requests.get(lexai_twitter_url,params=tweet_params).json()

'''
## Twitter says nothing
'''
#st.write('Tweets about this topic were liked by',tweet_likes[0], 'people on Twitter')

## EURLEX
'''
## REGULATIONS
'''
lexai_eurlex_url = "http://127.0.0.1:8000/query"
tweet_params=dict(query=query,n=5)
eurlex = requests.get(lexai_eurlex_url,params=tweet_params).json()
for i in eurlex:
    st.write(eurlex[i]['title'])
    st.write(eurlex[i]['author'])
    st.write(eurlex[i]['date'])
    st.write(eurlex[i]['link'])



## CONSULTS
'''
## OPEN CONSULTATIONS
'''
lexai_eurlex_url = "http://127.0.0.1:8000/query"
consults_params=dict(query=query,index='consultations',n=50)
consults = requests.get(lexai_eurlex_url,params=consults_params).json()
for i in consults:
    if consults[i]['status']=='OPEN':
        st.write('Title: ',consults[i]['title'])
        st.write('Type of act: ',consults[i]['type_of_act'])
        st.write('Start date: ',consults[i]['start_date'])
        st.write('End date: ',consults[i]['end_date'])
        st.write('Link: ',consults[i]['link'])