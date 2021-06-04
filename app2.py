import streamlit as st

'''
# LexAI
It's beautiful
'''

# API QUERIES
query = st.text_input("Search for a topic", 'agriculture')

import requests

#indices=['eurlex', 'consultations', 'twitter_query', 'twitter_press', 'twitter_politicians'])

'''
## REGULATIONS
'''
eurlex_url = "http://127.0.0.1:7700/indexes/eurlex/search"
eurlex_params=dict(q=query)
eurlex = requests.get(eurlex_url,params=eurlex_params).json()
st.write(eurlex)




