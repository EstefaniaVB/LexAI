import json
from twython import Twython
import pandas as pd

with open("twitter_credentials.json", "r") as file:
    creds = json.load(file)

python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])


def twitter_query(keyword, count):

    query = {'q': str(keyword),
            'result_type': 'popular',  # other options 'mixed'
            'count': count,   # max 100?
            # 'until':"2019-02-01",
            #'geocode': '50.0598058,14.3255426,2000km'
            }

    dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': [], 'user_loc': [], 'followers_count': [],
                'lang': [], 'user_desc': []}

    for status in python_tweets.search(**query)['statuses']:
        dict_['user'].append(status['user']['screen_name'])
        dict_['date'].append(status['created_at'])
        dict_['text'].append(status['text'])
        dict_['favorite_count'].append(status['favorite_count'])# Structure data in a pandas DataFrame for easier manipulation
        dict_['user_loc'].append( status['user']['location'])
        dict_['followers_count'].append(status['user']['followers_count'])
        dict_['lang'].append(status['lang'])
        dict_['user_desc'].append(status['user']['description'])
        
        df = pd.DataFrame(dict_)
    
    
    
    return df
