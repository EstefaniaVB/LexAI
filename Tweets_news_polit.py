import os
from os.path import join
from dotenv import load_dotenv
from twython import Twython
import pandas as pd
import os
import time

#Loading data
press=pd.read_csv("/Users/estefaniavidalbouzon/code/EstefaniaVB/LexAI/LexAI/raw_data/press.csv", delimiter=";")
meps=pd.read_csv("/Users/estefaniavidalbouzon/code/EstefaniaVB/LexAI/LexAI/raw_data/meps.csv", delimiter=",")

#Loading credentials (change the path to the .env file)
pwd ="/Users/estefaniavidalbouzon/code/EstefaniaVB/LexAI/LexAI/"
env_path = join(pwd,'.env') # ../.env
load_dotenv(dotenv_path=env_path)
inv = load_dotenv(dotenv_path=env_path)

#CREDENTIALS

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

python_tweets = Twython(CONSUMER_KEY, CONSUMER_SECRET)

### New outlets and politicians twitter data

news = press["TWITTER USERNAME "]
politicians = meps["twitter"]


#### Twitter limitation

#Limit of 100,000 requests per day to the /statuses/user_timeline endpoint, in addition to existing user-level and app-level rate limits. This limit is applied on a per-application basis, meaning that a single developer app can make up to 100,000 calls during any single 24-hour period.
#This method can only return up to 3,200 of a user's most recent Tweets. Native retweets of other statuses by the user is included in this total, regardless of whether include_rts is set to false when requesting this resource.


#- We can just retrieve 200 tweets/request
#- 900 tweets 15 min
#- 100000 in 24h

#We can make 4 request 200 tweets + 1 request 100 tweets each 15 minutes


#requesting the tweets from the news

def get_politicians_data():
    news_tweets=[]
    time.sleep(60*15) #run every 15min
    for outlet in news:
        news_tweets.append(python_tweets.get_user_timeline(screen_name=outlet, count=3))
        
    news_data = pd.DataFrame(news_tweets)
    return news_data
    



#Selecting relevant information

def get_news_data_filtered():
    data_new_filtered=[]
    for column in get_politicians_data():
        for row in get_politicians_data()[column]:
            id_new = row["id"]
            text = row["text"]
            try:
                url = row["entities"]["urls"][0]["url"]
            except:
                url =""
            try:
                expanded_url = row["entities"]["urls"][0]["expanded_url"]
            except:
                expanded_url =""
            name = row["user"]["name"]
            location = row["user"]["location"]
            followers_count = row["user"]["followers_count"]
            friends_count = row["user"]["friends_count"]
            listed_count = row["user"]["listed_count"]
            favourites_count = row["user"]["favourites_count"]
            profile_image_url = row["user"]["profile_image_url"]
            retweet_count= row["retweet_count"]
            source = row["source"]
            created_at = row["created_at"]
            
            data_new_filtered.append({"id_new":id_new,"text":text,"url":url,"expanded_url":expanded_url,"name":name,"location":location,"followers_count":followers_count,"friends_count":friends_count,"listed_count":listed_count,"favourites_count":favourites_count,"profile_image_url":profile_image_url,"retweet_count":retweet_count,"source":source,"created_at":created_at})
    news_tweets = pd.DataFrame(data_new_filtered)
    return news_tweets    

#requesting the tweets from the politicians

def get_politicians_data():
    meps_tweets = []
    time.sleep(60*15)
    for politic in politicians:
        print(f"Downloading tweets from: ...{politic}")
        meps_tweets.append(python_tweets.get_user_timeline(screen_name=politic, count=1))
    
    meps_data = pd.DataFrame(meps_tweets)
    return meps_data


def get_politicians_data_filtered():
    
    data_politicians_filtered=[]

    for column in get_politicians_data():
        for row in get_politicians_data()[column]:
            id_new = row["id"]
            text = row["text"]
            try:
                url = row["entities"]["urls"][0]["url"]
            except:
                url =""
            try:
                expanded_url = row["entities"]["urls"][0]["expanded_url"]
            except:
                expanded_url =""
            name = row["user"]["name"]
            location = row["user"]["location"]
            followers_count = row["user"]["followers_count"]
            friends_count = row["user"]["friends_count"]
            listed_count = row["user"]["listed_count"]
            favourites_count = row["user"]["favourites_count"]
            profile_image_url = row["user"]["profile_image_url"]
            retweet_count= row["retweet_count"]
            source = row["source"]
            created_at = row["created_at"]
            
            data_politicians_filtered.append({"id_new":id_new,"text":text,"url":url,"expanded_url":expanded_url,"name":name,"location":location,"followers_count":followers_count,"friends_count":friends_count,"listed_count":listed_count,"favourites_count":favourites_count,"profile_image_url":profile_image_url,"retweet_count":retweet_count,"source":source,"created_at":created_at})
    politicians_tweets = pd.DataFrame(data_politicians_filtered)
    return politicians_tweets
    
