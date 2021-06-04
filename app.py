import streamlit as st
'''
# LexAI Website !!!

It's beautiful
'''


# API QUERIES
query = st.text_input("Search for a topic", 'agriculture')

import requests


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
lexai_eurlex_url = "http://35.223.18.2/indexes/eurlex/search"
eurlex_params=dict(q=query)
headers={'X-Meili-API-Key':'OTkwNzQ0ZGRkZTc0NDcwM2RlMzFlOGIx'}
eurlex = requests.get(lexai_eurlex_url,params=eurlex_params,headers=headers).json()
st.write(eurlex)

