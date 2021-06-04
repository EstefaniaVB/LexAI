from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/query")
def query(query, index='eurlex', n=20):
    results = search.query_ms(query, index, int(n))
    return {i: result for i, result in enumerate(results)}

@app.get("/build")
def build(queries='default', pages=50, rebuild=0):    
    rebuild = True if rebuild == '1' else False
    return search.build_ms_many(queries, int(pages), rebuild)