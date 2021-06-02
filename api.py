from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from LexAI.twitterAPI import twitter_query
from LexAI.dbsearch import Search

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

search = Search()  # meilisearch searcher/builder

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
    return str(tweet_likes), str(tweet_followers)

@app.get("/query")
def query(query, index='eurlex', n=20):
    results = search.query_ms(query, index, int(n))
    return {i: result for i, result in enumerate(results)}

@app.get("/build")
<<<<<<< HEAD
def build(queries, pages=50, rebuild=0):
=======
def build(queries='default', pages=50, rebuild=0):
>>>>>>> ba42331d3018688202c1bcb27fce82d3b6762bad
    if queries == 'default':
        queries = [
            'agriculture',
            'energy',
            'technology',
            'finance',
            'law',
            'human rights',
            'worker rights',
            'fishing',
            'euro',
            'nuclear',
            'climate',
            'conservation',
            'environment',
            'politics',
            'tax'
        ]
<<<<<<< HEAD

    rebuild = True if rebuild == '1' else False
    #return search.build_ms_many(queries, int(pages), rebuild)
    return search.build_ms_many(queries, int(pages))
=======
    else:
        queries = queries.split(',')
    
    rebuild = True if rebuild == '1' else False
    return search.build_ms_many(queries, int(pages), rebuild)
>>>>>>> ba42331d3018688202c1bcb27fce82d3b6762bad
