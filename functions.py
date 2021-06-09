import pandas as pd
from geopy import geocoders
from geopy.geocoders import Nominatim
import math
import requests





def get_tweets(query,source):

  '''sources: twitter_query, twitter_politicians, twitter_press'''

  params=dict(q=query,limit=100000)
  headers={'X-Meili-API-Key':'OTkwNzQ0ZGRkZTc0NDcwM2RlMzFlOGIx'}
  lexai_url = f"http://35.223.18.2/indexes/{source}/search/"
  data = requests.get(lexai_url,params=params,headers=headers).json()
  data_df=pd.DataFrame(data['hits'])
  data_df = data_df[data_df["timestamp"] >= 1.622115e+09]   ###filters tweets from newer than certain timepoint ~27th may
  data_df = data_df.sort_values(by=['timestamp'])
  data_dict = data_df.to_dict('records')   #creates dictionary for further use
  return data_dict



def get_country(city):
    df_europe = pd.read_csv('list_cities3.csv', delimiter= ';')
    country = df_europe.loc[df_europe['city'] == city, 'country'].iloc[0]
    return country


def count_cities(tweets):
    
    #in the user locations sometimes its Paris, France, sometimes France
    # sometimes Paris, here we try to filter this for cities
    
    df_europe = pd.read_csv('list_cities3.csv', delimiter= ';')
    list_cities = list(df_europe['city'])
    list_countries = list(df_europe['country'])
    
    
    city_counts = {
    'city': [],
    'tweets':[],
    'likes': [],
    'retweets': [],
    'sentiment': []
    }
    
    
    for tweet in tweets:
        if ',' in tweet['user_loc']:
            list_loc = tweet['user_loc'].split(',')
            if list_loc[0] in list_cities:
                city_counts['city'].append(list_loc[0])
                city_counts['likes'].append(tweet['favorite_count'])
                city_counts['tweets'].append(1)
                city_counts['retweets'].append(tweet['retweet_count'])
                city_counts['sentiment'].append(tweet['compound_score'])
            
        elif tweet['user_loc'] in list_cities:
            city_counts['city'].append(tweet['user_loc'])
            city_counts['likes'].append(tweet['favorite_count'])
            city_counts['tweets'].append(1)
            city_counts['retweets'].append(tweet['retweet_count'])
            city_counts['sentiment'].append(tweet['compound_score'])
            
    df_city_counts = pd.DataFrame(city_counts)
    df_city_counts = df_city_counts.dropna()
    df_city_counts = df_city_counts.groupby(by="city", as_index=False).sum()
            
    return df_city_counts


    
def count_countries(tweets):
    
    df_europe = pd.read_csv('list_cities3.csv', delimiter= ';')
    list_cities = list(df_europe['city'])
    list_countries = list(df_europe['country'])
    
    country_counts = {
    
    'country': [],
    'tweets':[],
    'likes': [],
    'retweets': [],
    'sentiment': []
    }
    
    
    for tweet in tweets:
        if ',' in tweet['user_loc']:
            list_loc = tweet['user_loc'].split(',')
            if list_loc[1] in list_countries:
                country_counts['country'].append(list_loc[1])
                country_counts['likes'].append(tweet['favorite_count'])
                country_counts['tweets'].append(1)
                country_counts['retweets'].append(tweet['retweet_count'])
                country_counts['sentiment'].append(tweet['compound_score'])
                
            if list_loc[0] in list_cities:
                country_counts['country'].append(get_country(list_loc[0])) #translates city to country
                country_counts['likes'].append(tweet['favorite_count'])
                country_counts['tweets'].append(1)
                country_counts['retweets'].append(tweet['retweet_count'])
                country_counts['sentiment'].append(tweet['compound_score'])

            
            
        elif tweet['user_loc'] in list_cities:
            country_counts['country'].append(get_country(tweet['user_loc']))
            country_counts['likes'].append(tweet['favorite_count'])
            country_counts['tweets'].append(1)
            country_counts['retweets'].append(tweet['retweet_count'])
            country_counts['sentiment'].append(tweet['compound_score'])
            
        elif tweet['user_loc'] in list_countries:
            country_counts['country'].append(tweet['user_loc'])
            country_counts['likes'].append(tweet['favorite_count'])
            country_counts['tweets'].append(1)
            country_counts['retweets'].append(tweet['retweet_count'])
            country_counts['sentiment'].append(tweet['compound_score'])
            
    df_country_counts = pd.DataFrame(country_counts)
    df_country_counts = df_country_counts.dropna()
    df_country_counts = df_country_counts.groupby(by="country", as_index=False).sum()
    
    return df_country_counts
 
    
def add_radius(df):
    df["radius"] = df["retweets"].apply(lambda likes: math.sqrt(likes)*1000 + 10000)
    return df


##### define colors from sentiment ####

def sent_ref(df):
    df['sent_ref'] = df['sentiment'] / df['tweets']
    return df

def sent_color_green(sent):
    
    if sent > 0:
        green = 100
    else:
        green = 0
        
    return green


def sent_color_red(sent):
    
    if sent < 0:
        red = 100
    else:
        red = 0
    
    return red
    
    
def sent_color_blue(sent):
    blue = sent * 0
    return blue


def sent_shade(sent):
    if sent < 0:
        shade = -300 * sent + 50
    else:
        shade = 300 * sent + 50
    return shade
    
def sent_colors(df):
    df['r'] = df['sent_ref'].apply(sent_color_red)
    df['g'] = df['sent_ref'].apply(sent_color_green)
    df['b'] = df['sent_ref'].apply(sent_color_blue)
    df['s'] = df['sent_ref'].apply(sent_shade)
    df['sent_ref'] = df['sent_ref'].round(decimals=4)
    return df


def refine_cities(data_dict):

    #this function concludes the steps of summing the tweet counts, likes etc. 
    #by city in a dataframe and assign them to a latitude and longitude
    #to display the data on a geographical map
    #the data_dict argument must be a list of dictionaries, which is the output of the
    #get_tweets function

    df_cities_loc = pd.read_csv('city_loc.csv')
    

    df_cities = count_cities(data_dict)
    df_cities = df_cities.merge(df_cities_loc, how='left', on='city')
    df_cities = df_cities.dropna()
    df_cities = add_radius(df_cities)
    df_cities = sent_ref(df_cities)
    df_cities = sent_colors(df_cities)
    return df_cities


def refine_countries(data_dict):

    #does the same as refine_cities just for countries

    df_countries_loc = pd.read_csv('country_loc.csv')

    df_countries = count_countries(data_dict)
    df_countries = df_countries.merge(df_countries_loc, how='left', on='country')
    df_countries = df_countries.dropna()
    df_countries = add_radius(df_countries)
    df_countries = sent_ref(df_countries)
    df_countries = sent_colors(df_countries)
    return df_countries