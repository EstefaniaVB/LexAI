from os import environ
from google.cloud import translate
import json
from twython import Twython
import pandas as pd


# Enter your keys/secrets as strings in the following fields
credentials = {}
credentials['CONSUMER_KEY'] = ''
credentials['CONSUMER_SECRET'] = ''
credentials['ACCESS_TOKEN'] = '-'
credentials['ACCESS_SECRET'] = ''

#Save the credentials object to file
with open("twitter_credentials.json", "w") as file:
    json.dump(credentials, file)
    
with open("twitter_credentials.json", "r") as file:
    creds = json.load(file) 
    
python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])    



python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])    


def get_places():
    
    '''creates a list of places and countries in europe, for locality-filtering the output tweets'''
    cities = pd.read_csv('list_cities3.csv',delimiter=';')
    
    list_cities = list(cities['city'])
    list_cities = [element.lower() for element in list_cities]
    list_countries = list(set(cities['county']))
    list_countries = [element.lower() for element in list_countries]
    list_eur = list_cities + list_countries
    return list_eur


def gtrans(text,dest='en'):
    
    '''this function represents the google translate API. use wisely!
        its expensive (20$/1mio characters, makes only 5000 tweets)'''
    
    
    project_id = 'lewagon-bootcamp-timwolfram' #environ.get("PROJECT_ID", "")

    parent = f"projects/{project_id}"
    client = translate.TranslationServiceClient()


    sample_text = text
    target_language_code = dest

    response = client.translate_text(
        contents=[sample_text],
        target_language_code=target_language_code,
        parent=parent,
    )

    for translation in response.translations:
        output_trans = translation.translated_text
        
    return output_trans


def remove_duplicates(tweets):
    li = []
    for tweet in tweets:
        if not tweet in li:
            li.append(tweet)

    return li


def get_tweets(query,count,result_type='mixed'):   #count: max 10 because its looking for all 19 languages at once

    '''this function uses the twitter search endpoint with max 190 requests/15 min
    the output is a list of dictionaries with one dict per tweet.
    keys are the features of the tweets'''
    
    ''' it uses the google-translate API wich kosts 20$ per ~5000 tweets '''

    query_word = query
    count_tweets = count
    
    lang_list = ['en','de','fr','el','it','es',
                    'pl', 'ro', 'nl', 'hu','pt',
                    'sv',  'cs', 'bg', 'sk', 'da',
                    'fi', 'hr', 'lt'
                ]

    #dict_ = {}
    
    result_type = result_type # other options 'mixed','popular','recent'

    list_tweets = []

    for lang in lang_list:

        query_word = gtrans(query_word, dest=lang)
        if lang == 'en':
            query = {'q': query_word,
                'result_type': result_type,  
                'count': count_tweets,   # max 100
                'geocode': '51.51753,-0.11214,1000mi'
                }

        elif lang == 'fr':
            query = {'q': query_word,
                'result_type': result_type,  
                'count': count_tweets,   # max 100
                'geocode': '47.22283,2.07099,1000mi'
                }
        elif lang == 'es':
            query = {'q': query_word,
                'result_type': result_type,  
                'count': count_tweets,   # max 100
                'geocode': ' 40.42955,-3.67930,1000mi'
                }

        elif lang == 'pt':
            query = {'q': query_word,
                'result_type': result_type,  
                'count': count_tweets,   # max 100
                'geocode': '39.82059,-7.49342,1000mi'
                }

        else:
            query = {'q': query_word,
                'result_type': result_type,  # 
                'count': count_tweets,   # max 100
                #'geocode': '50.0598058,14.3255426,1000km'
                }


        for status in python_tweets.search(**query)['statuses']:
            dict_ = {}
            dict_['id'] = status['id']
            dict_['user'] = status['user']['screen_name']
            dict_['date'] = status['created_at']
            dict_['text'] = status['text']
            dict_['text_en'] = gtrans(str(status['text']), dest='en')
            dict_['favorite_count'] = status['favorite_count']
            dict_['user_loc'] =  status['user']['location']
            dict_['followers_count'] = status['user']['followers_count']
            dict_['lang'] = status['lang']
            dict_['user_desc'] = status['user']['description']
            try:
                dict_['user_desc_en'] = gtrans(str(status['user']['description']), dest='en')
            except:
                dict_['user_desc_en'] = 'none'
            dict_['user_verified'] = status['user']['verified']
            dict_['hashtags'] = status['entities']['hashtags']
            dict_['retweet_count'] = status['retweet_count']

            list_tweets.append(dict_) 
    
    return list_tweets


def local_filter(tweets, list_eur=get_places(), no_loc=True):
    
    '''filters the output of the get_tweets function to only get european posts'''
    
    if no_loc == True:
        list_eur.append('')
        
    for tweet in tweets:
        if not tweet['user_loc'].split(',')[0] in list_eur:
            tweets.remove(tweet)
        
        
    return tweets




