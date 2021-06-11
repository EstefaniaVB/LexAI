import json
import os
import sys
from collections import Counter
from os.path import dirname, exists, join

import gensim.downloader as api
import meilisearch
import nltk
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer

load_dotenv(dotenv_path=join(dirname(dirname(__file__)),'.env'))

class Analyse:
    
    def __init__(self, url='http://35.223.18.2', key=None):
        
        if key is None:
            key = os.getenv('MEILISEARCH_KEY')
        
        self.client = meilisearch.Client(url, key)
        self.indices = [idx.get('name', None) for idx in self.client.get_indexes()]
        
    @staticmethod
    def get_words():
        text_keys = {
            'eurlex': ['title'],
            'consultations': ['title', 'topics'],
            'twitter_query': ['text_en', 'user_desc_en'],
            'twitter_politicians': ['text_en', 'user_desc_en'],
            'twitter_press': ['text_en', 'user_desc_en']
        }
        
        print('Extracting all lemmatized words from json files... ', end='')
        folder = join(os.path.abspath(''), 'data.json')
        if not exists(folder):  # if folder doesn't exist
            print('Folder not found.')
            return

        files = os.listdir(folder)
        indices = [file.replace('.json', '') for file in files]
        if len(files) == 0:  # if no files
            print('No files found.')
            return

        words = []
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        tokenizer = nltk.RegexpTokenizer(r"\w+")

        for index, filename in zip(indices, files):
            with open(join(folder, filename), 'r') as file:
                json_ = json.load(file)

            for i in range(len(json_)):
                for key in text_keys[index]:
                    if json_[i][key] is not None:
                        text = json_[i][key].lower().replace(r'\d','')
                        tokens = [lemmatizer.lemmatize(word) for word in tokenizer.tokenize(text) if word not in stop_words]
                        words.extend(tokens)
        
        print('Done.\n')
        return words
    
    def get_synonyms(self, frac=0.03, n=0.5):
        words = self.get_words()
        
        print('Loading model... ', end='')
        word2vec_transfer = api.load('word2vec-google-news-300')
        print('Done.')
        
        print('Getting available words in model... ', end='')
        available_words = list(word2vec_transfer.key_to_index.keys())
        print('Done.')
        
        print('Extracting nouns and adjectives...', end='')
        words_to_keep = set([word for (word, tag) in nltk.pos_tag(words) if any(i in tag for i in ['NN', 'JJ'])])
        print('Done.')
        
        print('Filtering words... ', end='')
        word_counts = {k: v for k, v in Counter(words).items() if k in words_to_keep}
        if isinstance(frac, int):
            min_count = frac
        else:
            min_count = sorted(list(word_counts.values()))[::-1][int(len(word_counts.values()) * 0.03)]
        words = [word for word in words_to_keep if (word_counts[word] > min_count and word in available_words)]
        print('Done.')
        
        print('Finding synonyms... ', end='')
        if n >= 1:
            synonyms = {word: list(np.array(word2vec_transfer.most_similar(word, topn=n))[:,0]) for word in words}
        else:
            synonyms = {}
            for word in words:
                arr = np.array(word2vec_transfer.most_similar(word, topn=20))
                synonyms[word] = list(arr[arr[:,1].astype(float) > n][:,0])
        print('Done.')
        
        folder = join(os.path.abspath(''), 'data.json')
        with open(join(folder, 'synonyms.json'), 'w') as file:
            json.dump(synonyms, file)
        
        print('Saved synonyms to data.json/synonyms.json\n')
        return synonyms
    
    def get_all_sentiments(self):
        folder = dirname(dirname(__file__))
        if not exists(folder):  # if folder doesn't exist
            print('Folder not found.')
            return
        
        files = os.listdir(folder)
        indices = [file.replace('.json', '') for file in files]
        
        if len(files) == 0:  # if no files
            print('No files found.')
            return
        
        for index, filename in zip(indices, files):
            filepath = join(folder, 'data.json', filename)
            with open(filepath, 'r') as file:
                documents = json.load(file)
            
            filepath = join(folder, 'update.json', f'{index}_sentiment.json')
            with open(filepath, 'w') as file:
                json.dump(self.get_sentiments(documents), file)

    
    def get_sentiments(self, data):
        #initialize sentiment analyzer
        sid = SentimentIntensityAnalyzer()

        # make dict of scores
        sentiments = {i : {'id': doc['id'], 
                           'compound_score': sid.polarity_scores(doc['text_en'])['compound']}
                      for i, doc in data.items()}

        # add category
        for k, v in sentiments.items():
            if sentiments[k]['compound_score'] <= -0.2:
                sentiments[k]['sentiment'] = 'negative'
            elif sentiments[k]['compound_score'] > 0.2:
                sentiments[k]['sentiment'] = 'positive'
            else:
                sentiments[k]['sentiment'] = 'neutral'
            
        return sentiments

if __name__ == '__main__':
    if len(sys.argv) > 2:
        try:
            kwargs = {kwarg.split("=")[0]: eval(kwarg.split("=")[1]) for kwarg in sys.argv[2:]}
        except NameError:
            kwargs = {kwarg.split("=")[0]: kwarg.split("=")[1].split(",") for kwarg in sys.argv[2:]}
        getattr(Analyse(), sys.argv[1])(**kwargs)
    elif len(sys.argv) == 2:
        getattr(Analyse(), sys.argv[1])()
