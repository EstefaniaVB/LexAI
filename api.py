from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from LexAI.twitterAPI import twitter_query

#from predictions import get_prediction
#from consultations import get_consultation
#from twitterapi import get_tweet_volume

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create root endpoint
@app.get("/")
def index():
    return {"greeting": "Hello Estefania"}

# Predict endpoint
@app.get("/predict")
def predict(keyword):
    #PSEUDO-CODE
    #Regulations list
        #regulations=get_regulation(keyword)
    #Consultations list
        #consultations=get_consultation(keyword)
    #Twitter list
    tweets=twitter_query(keyword,10)
    tweet_likes=tweets['favorite_count'].sum()
    tweet_followers=tweets['followers_count'].sum()
    #return regulations,consultations,tweet_volume

    # print keyword entered by user
    return str(tweet_likes),str(tweet_followers)
