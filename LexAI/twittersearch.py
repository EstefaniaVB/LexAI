import os
import re
from datetime import datetime
from itertools import chain
from os.path import dirname, join
from time import mktime, sleep
from unicodedata import normalize

import pandas as pd
from dotenv import load_dotenv
from google.cloud import translate
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from twython import Twython

load_dotenv(dotenv_path=join(dirname(dirname(__file__)),'.env'))

class TwitterSearch:
    #### Twitter limitation

    # Limit of 100,000 requests per day to the /statuses/user_timeline endpoint, 
    # in addition to existing user-level and app-level rate limits. This limit 
    # is applied on a per-application basis, meaning that a single developer app 
    # can make up to 100,000 calls during any single 24-hour period.
    
    # This method can only return up to 3,200 of a user's most recent Tweets. 
    # Native retweets of other statuses by the user is included in this total, 
    # regardless of whether include_rts is set to false when requesting this resource.

    #- We can just retrieve 200 tweets/request
    #- 900 tweets 15 min
    #- 100000 in 24h

    def __init__(self, id_key='PROJECT_E', trans=False):
        # Enter your keys/secrets as strings in the following fields
        self.trans = trans
        
        self.creds = {}
        self.creds['CONSUMER_KEY'] = os.getenv('CONSUMER_KEY')
        self.creds['CONSUMER_SECRET'] = os.getenv('CONSUMER_SECRET')
        self.creds['ACCESS_TOKEN'] = os.getenv('ACCESS_TOKEN')
        self.creds['ACCESS_SECRET'] = os.getenv('ACCESS_SECRET')
        
        self.python_tweets = Twython(self.creds['CONSUMER_KEY'],
                                     self.creds['CONSUMER_SECRET'])
        
        project_id = os.getenv('PROJECT_E')  # change to your project ID env key
        self.parent = f"projects/{project_id}"
        self.g_client = translate.TranslationServiceClient()
        
    def load_users(self):
        ### New outlets and politicians twitter data
        press = pd.read_csv(join(dirname(__file__), 'data/press.csv'), delimiter=",")
        meps = pd.read_csv(join(dirname(__file__), 'data/meps.csv'), delimiter=",")
        press = press.dropna(how='any', subset=['twitter'])
        meps = meps.dropna(how='any', subset=['twitter'])

        return press, meps
        
    def extract_info(self, result, df):
        entry = {}
    
        entry['id'] = result['id']
        entry['user'] = result['user']['screen_name']
        text = normalize('NFKD', result['full_text'])
        entry['text'] = re.sub(r'https?:\/\/\S*', '', text, flags=re.MULTILINE)
        entry['text_en'] = self.gtrans(entry['text'], dest='en')
        
        dt = datetime.strptime(result['created_at'],
                                "%a %b %d %H:%M:%S %z %Y")
        entry['date'] = datetime.strftime(dt, "%Y/%m/%d %H:%M:%S")
        entry['lang'] = result['lang']
        entry['iso_lang'] = result.get('metadata', {}).get('iso_language_code', None)
        
        entry['user_verified'] = result['user']['verified']
        entry['followers_count'] = result['user']['followers_count']
        entry['user_loc'] =  normalize('NFKD', result['user']['location'])
        entry['user_desc'] = normalize('NFKD', result['user']['description'])
        entry['user_desc_en'] = self.gtrans(entry['user_desc'], dest='en')
        entry['user_image'] = result['user']['profile_image_url']
        
        entry['hashtags'] = ', '.join([i['text'] 
                                        for i in result['entities']['hashtags']])
        entry['mentions'] = ', '.join([i['screen_name'] 
                                        for i in result['entities']['user_mentions']])
        entry['retweet_count'] = result['retweet_count']
        entry['favorite_count'] = result['favorite_count']
        
        entry['timestamp'] = mktime(dt.timetuple())
        entry['link'] = f"https://twitter.com/{entry['user']}/status/{entry['id']}"

        user = entry['user'].lower().strip()
        if all(col in df.columns for col in ['name', 'country', 'eu_group', 'national_group']):
            entry['name'] = df[df['twitter'].str.lower() == user]['name'].iloc[0]
            entry['country'] = df[df['twitter'].str.lower() == user]['country'].iloc[0]
            entry['eu_group'] = df[df['twitter'].str.lower() == user]['eu_group'].iloc[0]
            entry['national_group'] = df[df['twitter'].str.lower() == user]['national_group'].iloc[0]
        elif 'media' in df.columns:
            entry['name'] = df[df['twitter'].str.lower() == user]['media'].iloc[0]
            entry['country'] = df[df['twitter'].str.lower() == user]['country'].iloc[0]
        
        if entry['text_en'] is not None:
            sid = SentimentIntensityAnalyzer()
            entry['compound_score'] = sid.polarity_scores(entry['text_en'])['compound']
            if entry['compound_score'] <= -0.2:
                entry['sentiment'] = 'negative'
            elif entry['compound_score'] > 0.2:
                entry['sentiment'] = 'positive'
            else:
                entry['sentiment'] = 'neutral'
        
        return entry

    def gtrans(self, text, dest='en'):
        '''this function represents the google translate API. use wisely!
        its expensive (20$/1mio characters, makes only 5000 tweets).'''
        if not self.trans:
            return
        elif len(text) == 0:
            print(datetime.now().strftime("%H:%M:%S: "), 'No text to translate')
            return

        response = self.g_client.translate_text(contents=[text], 
                                                target_language_code=dest, 
                                                parent=self.parent)

        for translation in response.translations:
            output_trans = translation.translated_text
            
        if output_trans is None:
            print(datetime.now().strftime("%H:%M:%S: "), 'ERROR: no translation given')

        return output_trans

    def search_query(self, query, count=5, result_type='recent', lang=None):
        # count: max 10 because its looking for all 19 languages at once
        '''this function uses the twitter search endpoint with max 190 requests/15 min
        the output is a list of dictionaries with one dict per tweet.
        keys are the features of the tweets
        
        it uses the google-translate API wich kosts 20$ per ~5000 tweets 
        result_type options 'mixed','popular','recent' '''
        
        if lang is None:
            lang_list = ['en','de','fr','el','it','es', 'pl', 'ro', 'nl', 'hu', 
                         'pt', 'sv', 'cs', 'bg', 'sk', 'da', 'fi', 'hr', 'lt']
        elif isinstance(lang, list):
            lang_list = [l.lower() for l in lang]
        else:
            lang_list = [lang.lower()]
        
        geocode = {'en': '51.51753,-0.11214,1000km',
                   'fr': '47.22283,2.07099,1000km',
                   'es': '40.42955,-3.67930,1000km',
                   'pt': '39.82059,-7.49342,1000km',
                   'other': '50.0598058,14.3255426,1000km'}
        
        tweets = []
        print('Searched query in languages:', end='')
        for lang in lang_list:
            print(lang, end=', ')
            query_trans = self.gtrans(query, dest=lang)

            params = {'q': query_trans,
                      'result_type': result_type, 
                      'count': count,
                      'tweet_mode': 'extended'}
            #if geocode.get(lang, None) is not None:  # returns no tweets if used
            #    params['geocode'] = geocode.get(lang, None)
            
            results = self.python_tweets.search(**params)['statuses']
            if len(results) != 0:
                df = pd.DataFrame()
                tweets.extend([self.extract_info(result, df) for result in results])
        print()
        return tweets

    def search_username(self, usernames=None, count=10):
        if usernames == None:
            print('ERROR: No usernames defined')
            return None
        elif usernames == 'press':
            df = self.load_users()[0]
            usernames = list(df['twitter'])
        elif usernames == 'politicians':
            df = self.load_users()[1]
            usernames = list(df['twitter'])
        elif not isinstance(usernames, list):
            df = pd.DataFrame()
            usernames = usernames.split(',')
        
        print(f'\nSearching {len(usernames)} users\n')
        tweets = []
        for i, username in enumerate(usernames):
            if i % 10 == 0:
                print(f'Processed {i} users')

            query = {'screen_name': username,
                     'count': count,
                     'tweet_mode': 'extended'}
            
            # feature not currently working
            """
            start_t = int(datetime.now().strftime("%s"))
            end_t = start_t
            results = []
            

            while len(results) == 0 and end_t - start_t < 20*60: 
            """
            try:
                results = self.python_tweets.get_user_timeline(**query)
            except Exception:
                # break
                continue 
            
            if not len(results) == 0:
                tweets.extend([self.extract_info(result, df) for result in results])
                
                # feature not currently working
                """
                else:
                    print(datetime.now().strftime("%H:%M:%S:"),
                          'Twitter API limit reached. Retrying in 60s',
                          f'(Attempt {(end_t - start_t)//60}/20)')
                    sleep(60)
                    end_t = int(datetime.now().strftime("%s"))
                """
        print('Processed all users')
        return tweets
    

