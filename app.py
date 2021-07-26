import streamlit as st
from multiapp import MultiApp
from apps import home, data, model # import your app modules here

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
#components.html('<div style="position: relative; width: 100%; height: 0; padding-top: 100.0000%; padding-bottom: 48px; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden; border-radius: 8px; will-change: transform;">  <iframe style="position: absolute; width: 100%; height: 50%; top: 0; left: 0; border: none; padding: 0;margin: 0;"    src="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAEfatHdF58&#x2F;view?embed">  </iframe></div><a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAEfatHdF58&#x2F;view?utm_content=DAEfatHdF58&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">LexAI</a> de Estefanía Vidal Bouzón')
st.image('Images/LexAI2.png', width=200)
#st.subheader('Navigating public fora')

app = MultiApp()

# Add all your application here
app.add_app("Regulation", data.app)
app.add_app("Social Media", model.app)
# The main app
app.run()
