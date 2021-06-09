import streamlit as st
from multiapp import MultiApp
from apps import home, data, model # import your app modules here

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

app = MultiApp()

# Add all your application here
app.add_app("Regulations", data.app)
app.add_app("Opinions", model.app)
# The main app
app.run()
