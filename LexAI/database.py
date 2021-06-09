import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from os.path import dirname, exists, join
from time import mktime, sleep
from unicodedata import normalize

import gensim.downloader as api
import meilisearch
import numpy as np
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords

from LexAI.analyse import Analyse
from LexAI.twittersearch import TwitterSearch

load_dotenv(dotenv_path=join(dirname(dirname(__file__)),'.env'))

class Database(TwitterSearch, Analyse):
    
    def __init__(self, url='http://35.223.18.2', key=None, trans=True,
                 indices=['eurlex', 'consultations', 'twitter_query', 'twitter_press', 'twitter_politicians']):

        if key is None:
            key = os.getenv('MEILISEARCH_KEY')
        
        super().__init__('PROJECT_T', trans)
        super().__init__(url, key)
        project_id = os.getenv('PROJECT_E')  # change to your project ID env key
        self.parent = f"projects/{project_id}"
        
        self.client = meilisearch.Client(url, key)
        self.indices = indices
        self.trans = trans
        """ # NOT WORKING
        ms_indices = [idx.get('name', None) for idx in self.client.get_indexes()]

        for index in indices:
            if index not in ms_indices:
                self.client.create_index(index, {'primaryKey': 'id'})
                print(f'Created index: {index}')
        """
        
        self.client.index('eurlex').update_settings({
            'searchableAttributes': ['title', 'author', 'date', 'timestamp'],
            'rankingRules': ['typo', 'words', 'proximity', 'attribute', 
                             'wordsPosition', 'exactness', 'desc(timestamp)']})

        self.client.index('consultations').update_settings({
            'searchableAttributes': ['title', 'topics', 'type_of_act', 'status',
                                     'start_date', 'start_timestamp', 'end_date', 
                                     'end_timestamp'],
            'rankingRules': ['typo', 'words', 'proximity', 'attribute', 
                             'wordsPosition', 'exactness', 'desc(start_timestamp)', 
                             'desc(end_timestamp)']})
        
        for index in indices[2:]:
            self.client.index(index).update_settings({
                'rankingRules': ['typo', 'words', 'proximity', 'attribute', 
                                 'wordsPosition', 'exactness', 'desc(timestamp)']})

        self.log = {}

    def search_eurlex(self, query, page=1, lang='en', year=None):
        url = "https://eur-lex.europa.eu/search.html"

        params = {
            "scope": "EURLEX",
            "text": query,
            "lang": lang,
            "type": "quick",
            "DTS_DOM": "EU_LAW",
            "sortOne": "DD",
            "sortOneOrder": "desc",
            "page": page,
            "DD_YEAR": year
        }

        r = requests.get(url, params=params)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        if 'No results found.' in str(soup.find_all('div', class_='alert alert-info')):
            return
        
        
        page_results = soup.find_all('div', class_='SearchResult')
        final_results = []
        
        for result in page_results:
            entry = {}
            
            celex = result.find_all('div', class_='col-sm-6')[0].find('dd')
            celex = result.find('p').text if celex is None else celex.text
            celex = re.sub(r'[^a-zA-Z0-9]', '', celex)
            
            title = result.find('a', class_='title')
            col2 = result.find_all('div', class_='col-sm-6')[1].find_all('dd')
            date = list(filter(lambda v: re.match("\d{2}/\d{2}/\d{4}", v.text), col2))[0]
            dt = datetime.strptime(normalize('NFKD', date.text[:10]), "%d/%m/%Y")
            
            entry['id'] = normalize('NFKD', celex)
            entry['title'] = normalize('NFKD', title.text)
            entry['author'] = normalize('NFKD', col2[0].text)
            entry['date'] = datetime.strftime(dt, "%Y/%m/%d")
            entry['timestamp'] = mktime(dt.timetuple())
            entry['link'] = normalize('NFKD', title['name'])
            final_results.append(entry)
        return final_results
    
    def search_consultations(self, query, page=0, size=50, lang="EN"):
        url = "https://ec.europa.eu/info/law/better-regulation/brpapi/searchInitiatives"
        
        params = {
            'text': query,
            'page': page,
            'size': size,
            'language': lang
        }
 
        r = requests.get(url, params=params).json()

        try:
            content = r["_embedded"]
        except KeyError:
            return
        
        if r.get('status_code', None) == 500:
            return
        
        final_results = []
        
        for res in content["initiativeResultDtoes"]:
            entry = {}
            
            entry['id'] = res.get("id", None)
            entry['title'] = res.get("shortTitle", None)
            entry['type_of_act'] = res.get("foreseenActType", None)
            topics = res.get("topics", []) if len(res.get("topics", [])) != 0 else [{}]
            entry['topics'] = topics[0].get("label", None)
            
            status = res.get("currentStatuses", [])
            if len(status) != 0:
                entry['status'] = status[0].get("receivingFeedbackStatus", None)
                start_date = status[0].get("feedbackStartDate", None)
                end_date = status[0].get("feedbackEndDate", None)
            else:
                entry['status'] = None
                start_date = None
                end_date = None
            
            if start_date is not None:
                entry['start_date'] = start_date[:10]
                ts = mktime(datetime.strptime(start_date, "%Y/%m/%d %H:%M:%S").timetuple())
                entry['start_timestamp'] = ts
            else:
                entry['start_date'] = None
                entry['start_timestamp'] = 0
                
            if end_date is not None:
                entry['end_date'] = end_date[:10]
                ts = mktime(datetime.strptime(end_date, "%Y/%m/%d %H:%M:%S").timetuple())
                entry['end_timestamp'] = ts
            else:
                entry['end_date'] = None
                entry['end_timestamp'] = 0

            
            # links sometimes don't work, plz fix :)
            link_url = "https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/"
            title_link = entry['title'].replace(" ","-")
            entry['link']= f"{link_url}{entry['id']}-{title_link}_en"
            
            final_results.append(entry)
        return final_results

    def search_many(self, query, pages=10, index='eurlex', **params):
        results = []
        for page in range(pages):
            if index == 'eurlex':
                page_results = self.search_eurlex(query, page+1, **params)
            elif index == 'consultations':
                page_results = self.search_consultations(query, page, **params)
            else:
                return "Error: index not recognised"
                
            if page_results is not None:
                results.extend(page_results)
            else:
                print(f"Stopping at page {page}. No more results found.")
                break
        return results

    def build_ms(self, query, pages=10, index='eurlex', **params):
        db = self.client.index(index)
        start_len = db.get_stats()['numberOfDocuments']
        documents = []
        
        start_t = int(datetime.now().strftime("%s"))
        end_t = start_t
        
        while len(documents) == 0 and end_t - start_t < 20*60:
            if 'twitter' in index:
                if 'query' in index:
                    documents = self.search_query(query, count=pages, **params)
                else:
                    documents = self.search_username(query, count=pages)
                
                if len(documents) == 0:
                    print(datetime.now().strftime("%H:%M:%S:"),
                          'Twitter API limit reached. Retrying in 60s',
                          f'(Attempt {(end_t - start_t)//60}/20)')
                    sleep(60)
                    end_t = int(datetime.now().strftime("%s"))
                    continue
            else:
                documents = self.search_many(query, pages, index, **params)

            update_id = db.add_documents(documents)['updateId']
            
            while db.get_update_status(update_id)['status'] != 'processed':
                sleep(0.1)
            end_len = db.get_stats()['numberOfDocuments']
        
        return f"Found {len(documents)} results. Added {end_len - start_len} new entries to {index} index"

    def build_ms_many(self, queries='default', pages=50, indices=None, rebuild=0, **params):
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
        elif not isinstance(queries, list):
            queries = queries.split(',')
        pages = int(pages)
        
        if indices is None:
            indices = self.indices
        elif not isinstance(indices, list):
            indices = indices.split(',')
        
        for index in indices:
            db = self.client.index(index)
            if rebuild:
                update_id = db.delete_all_documents()['updateId']
                while db.get_update_status(update_id)['status'] != 'processed':
                    sleep(0.1)
                print(f'Deleted all documents from {index} index')
            
            self.log[index] = {}
            self.log[index]['rebuild'] = rebuild
            start_len = db.get_stats()['numberOfDocuments']
            
            if not any(i in index for i in ['press', 'politicians']):
                for query in queries:
                    print(f"Searching {pages} pages/tweets for {query} in {index}. ")
                    result = self.build_ms(query, pages, index, **params)
                    self.log[index][query] = result
                    print(result, '\n')
            else:
                queries = index.replace('twitter_', '')
                print(f"Searching {pages} tweets for {queries} in {index}. ")
                result = self.build_ms(queries, pages, index, **params)
                self.log[index]['result'] = result
                print(result, '\n')
            
            end_len = db.get_stats()['numberOfDocuments']
            idx_result = f"Total: {end_len - start_len} new entries added to {index} index\n"
            
            self.log[index]['complete'] = idx_result
            print(idx_result)
        
        if rebuild:
            self.get_synonyms()
        
        return self.log

    def query_ms(self, query, index='eurlex', n=20):
        if index not in self.indices:
            return [{"Error": "index not recognised"}]
        else:
            return self.client.index(index).search(query, {'limit': n})['hits']
    
    def check_folder(self, folder):
        folder = join(dirname(dirname(__file__)), folder)
        if not exists(folder):  # if folder doesn't exist
            os.makedirs(folder)  # create folder
        return folder
        
    def get_info(self, folder, indices=None):
        folder = self.check_folder(folder)
        files = os.listdir(folder)
        if indices is None:
            indices = [file.replace('.json', '') for file in files]
        else:
            indices = [file.replace('.json', '') for file in files 
                       if file.replace('.json', '') in indices]
        
        return folder, files, indices
        
    def export_json(self, indices=None):
        if indices is None:
            indices = [idx['uid'] for idx in self.client.get_indexes()]
        elif not isinstance(indices, list):
            indices = indices.split(',')
        
        folder = self.check_folder('data.json')
        
        for index in indices:          
            print(f'\nProcessing {index}')
            size = self.client.index(index).get_stats().get('numberOfDocuments', 0)
            export = self.client.index(index).get_documents({'limit':size})
            
            filepath = join(folder, f'{index}.json')
            with open(filepath, 'w') as file:
                json.dump(export, file)
            print(f'Exported {size} entries from {index} to data.json/{index}.json')
        
        self.get_synonyms_from_ms()
            
    def get_synonyms_from_ms(self):
        synonyms = self.client.index('eurlex').get_synonyms()
        
        folder = join(dirname(dirname(__file__)), 'update.json')
        with open(join(folder, 'synonyms.json'), 'w') as file:
            json.dump(synonyms, file)
        print('\nSaved synonyms to update.json/synonyms.json')
    
    def import_json(self, indices=None, replace=False):
        folder, files, indices = self.get_info('data.json')
        if len(files) == 0:  # if no files
            print('No files found.')
            return
        
        for index, filename in zip(indices, files):
            with open(join(folder, filename), 'r') as file:
                documents = json.load(file)
 
            try:
                self.client.create_index(index, {'primaryKey': 'id'})
                print(f'Created {index} index')
            except Exception:
                pass
            
            db = self.client.index(index)

            if replace:
                update_id = db.delete_all_documents()['updateId']
                while db.get_update_status(update_id)['status'] != 'processed':
                    sleep(0.1)
                print(f'\nDeleted all documents from {index} index')
                
            print(f'\n{filename} contains {len(documents)} entries')
            
            start_len = db.get_stats()['numberOfDocuments']
            update_id = db.add_documents(documents)['updateId']
            while db.get_update_status(update_id)['status'] != 'processed':
                sleep(0.1)
                if db.get_update_status(update_id)['status'] == 'failed':
                    break
            
            end_len = db.get_stats()['numberOfDocuments']
            print(f'Imported {end_len - start_len} entries to {index}')
    
    def import_updates(self, replace=False):
        folder, files, indices = self.get_info('update.json')
        if len(files) == 0:  # if no files
            print('No files found.')
            return
        
        for index, filename in zip(indices, files):
            with open(join(folder, filename), 'r') as file:
                documents = list(json.load(file).values())
            
            if index == 'synonyms':
                for idx in set(indices) - set(['synonym']):
                    if replace:
                        self.client.index(idx).reset_synonyms()
                        print(f'Deleted all synonyms')
                    self.client.index(idx).update_synonyms(documents)
                    self.client.index(idx).update_settings({'stopWords': stopwords.words('english')})
                print(f'Updated synonyms and stop words')
                continue
            if index not in [idx['uid'] for idx in self.client.get_indexes()]:
                print(f'\nERROR: Index {index} not found in database. Skipping {index}.\n')
                continue
            
            print(f'\n{filename} contains {len(documents)} entries. Updating...', end='')
            self.client.index(index).update_documents(documents)
            print(f'Done.')
    
    def import_data(self, index):
        index = index[0]
        if index == 'twitter_politicians':
            df = self.load_users()[1]
            df['twitter'] = df['twitter'].str.lower()
            
            print('Getting users... ', end='')
            users = {doc['id']: doc['user'].lower() for doc in self.client.index(index).get_documents({'limit': 9999999999})}
            documents = []
            print('Done.')
            
            for id, user in users.items():
                entry = {}
                entry['id'] = id
                entry['name'] = df[df['twitter'] == user]['name'].iloc[0]
                entry['country'] = df[df['twitter'] == user]['country'].iloc[0]
                entry['eu_group'] = df[df['twitter'] == user]['eu_group'].iloc[0]
                entry['national_group'] = df[df['twitter'] == user]['national_group'].iloc[0]
                
                documents.append(entry)
        elif index == 'twitter_press':
            df = self.load_users()[0]
            df['twitter'] = df['twitter'].str.lower()
            
            print('Getting users... ', end='')
            users = {doc['id']: doc['user'].lower() for doc in self.client.index(index).get_documents({'limit': 9999999999})}
            documents = []
            print('Done.')
            
            for id, user in users.items():
                entry = {}
                entry['id'] = id
                entry['name'] = df[df['twitter'] == user]['media'].iloc[0]
                
                documents.append(entry)
        else:
            print('ERROR: bad index.')
            return
        
        print(f'Updating {len(documents)} documents in {index}... ', end='')
        self.client.index(index).update_documents(documents)
        print('Done.\n')



if __name__ == '__main__':
    if len(sys.argv) > 2:
        try:
            kwargs = {kwarg.split("=")[0]: eval(kwarg.split("=")[1]) for kwarg in sys.argv[2:]}
        except NameError:
            kwargs = {kwarg.split("=")[0]: kwarg.split("=")[1].split(",") for kwarg in sys.argv[2:]}
        getattr(Database(), sys.argv[1])(**kwargs)
    elif len(sys.argv) == 2:
        getattr(Database(), sys.argv[1])()

