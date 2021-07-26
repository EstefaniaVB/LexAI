import pandas as pd
import math
import requests


def get_tweets(query,source):

  '''sources: twitter_query, twitter_politicians, twitter_press'''

  params=dict(q=query,limit=100000)
  headers={'X-Meili-API-Key':'OTkwNzQ0ZGRkZTc0NDcwM2RlMzFlOGIx'}
  lexai_url = f"http://127.0.0.1:7700/indexes/{source}/search/"
  data = requests.get(lexai_url,params=params,headers=headers).json()
  data_df=pd.DataFrame(data['hits'])
  data_df = data_df[data_df["timestamp"] >= 1.622115e+09]   ###filters tweets which are newer than certain timepoint ~27th may
  data_df = data_df.sort_values(by=['timestamp'])
  data_dict = data_df.to_dict('records')   #creates dictionary for further use
  return data_dict


def clean_and_sum(df, region):
    df = df.dropna()
    df['sentiment'] = df['sentiment'] * (df['retweets']+1) #scores sentiment of a tweet by retweet_count
    df = df.groupby(by=region, as_index=False).sum()
    df['sentiment'] = df['sentiment'] / df['tweets']
    df['sentiment'] = df['sentiment'].round(decimals=1)

    return df


def get_country(city):

    #takes a city as input and give the assigned country as output

    df_europe = pd.read_csv('list_cities3.csv', delimiter= ';')
    country = df_europe.loc[df_europe['city'] == city, 'country'].iloc[0]
    return country


def count_cities(tweets):
    
    #in the user_location-column, sometimes its Paris, France, sometimes France
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
    df_city_counts = clean_and_sum(df_city_counts, 'city')

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
    df_country_counts = clean_and_sum(df_country_counts, 'country')
    
    return df_country_counts
 
   
def add_radius(df):
    df["radius"] = df["retweets"].apply(lambda retweets: math.sqrt(retweets)*2000 + 20000)
    return df


##### define colors from sentiment ####


def sent_color_red(sent):
    
    if sent > 0:
        red = 96
    else:
        red = 115
    
    return red
    

def sent_color_green(sent):
    
    if sent > 0:
        green = 130
    else:
        green = 31
        
    return green

    
def sent_color_blue(sent):
    if sent > 0:
        blue = 253
    else:
        blue = 125
    
    return blue


def sent_shade(sent):
    if sent < 0:
        shade = 50 * math.sqrt(-sent) + 50
    else:
        shade = 50 * math.sqrt(sent) + 50
    return shade
    
    
def sent_colors(df):
    df['r'] = df['sentiment'].apply(sent_color_red)
    df['g'] = df['sentiment'].apply(sent_color_green)
    df['b'] = df['sentiment'].apply(sent_color_blue)
    df['s'] = df['sentiment'].apply(sent_shade)
    df['sentiment'] = df['sentiment'].round(decimals=4)
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
    df_cities = sent_colors(df_cities)
    return df_cities


def refine_countries(data_dict):

    #does the same as refine_cities just for countries

    df_countries_loc = pd.read_csv('country_loc.csv')

    df_countries = count_countries(data_dict)
    df_countries = df_countries.merge(df_countries_loc, how='left', on='country')
    df_countries = df_countries.dropna()
    df_countries = add_radius(df_countries)
    df_countries = sent_colors(df_countries)
    return df_countries

def refine_pol_press(data_dict):

    #this function concludes the steps of summing the tweet counts, likes etc. 
    #by city in a dataframe and assign them to a latitude and longitude
    #to display the data on a geographical map
    
    df = pd.DataFrame(data_dict)

    df = df[['retweet_count', 'favorite_count', 'compound_score', 'country']]
    df = df.rename(columns={"retweet_count": "retweets", "favorite_count": "likes", "compound_score": "sentiment"})
    df['tweets'] = 1
    df = clean_and_sum(df, 'country')

    df_countries_loc = pd.read_csv('country_loc.csv')

    
    df = df.merge(df_countries_loc, how='left', on='country')
    df = df.dropna()
    df = add_radius(df)
    df = sent_colors(df)
    return df