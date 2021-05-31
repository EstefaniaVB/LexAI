from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    return {"greeting": "Hello world"}

# Predict endpoint
@app.get("/predict")
def predict(keyword):
    #PSEUDO-CODE
    #Regulations list
        #regulations=get_regulation(keyword)
    #Consultations list
        #consultations=get_consultation(keyword)
    #Twitter list
        #tweet_volume=get_tweet_volume(keyword)
        #return regulations,consultations,tweet_volume

    # print keyword entered by user
    return {'keyword': keyword}
