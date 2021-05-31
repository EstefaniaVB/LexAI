'''in this file were the twitter requests are written'''

import tweepy
import pandas as pd

consumer_key = 
consumer_secret = 
access_token = 
access_token_secret = 

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
user = api.get_user('twitter')



def get_tweets():

    '''looking for tweets containing a key word 
    and list them in a dataframe with likes and date'''
    
    number_of_tweets = 50
    tweets = []
    likes = []
    time = []

    for i in tweepy.Cursor(api.search, q='agriculture',result_type='popular', tweet_mode="extended").items(number_of_tweets):
        tweets.append(i.full_text)
        likes.append(i.favorite_count)
        time.append(i.created_at)
        
    df = pd.DataFrame({'tweets':tweets, 'likes':likes, 'time':time})
    return df

