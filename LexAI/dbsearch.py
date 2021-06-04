import json
import os
import re
import sys
from datetime import datetime
from os.path import dirname, exists, join
from time import mktime, sleep
from unicodedata import normalize

import meilisearch
import requests
from bs4 import BeautifulSoup

from LexAI.twittersearch import TwitterSearch


class Search(TwitterSearch):
    
    def __init__(self, url='http://127.0.0.1:7700', key='',
                 indices=['eurlex', 'consultations', 'twitter_query', 
                          'twitter_press', 'twitter_politicians'],
                 trans=False):
        
        ## run in terminal
        # curl -L https://install.meilisearch.com | sh
        # ./meilisearch
        
        super().__init__()
        self.client = meilisearch.Client(url, key)
        self.indices = indices
        self.trans = trans
        for index in indices:
            try:
                self.client.create_index(index)
                print(f'Created {index} index')
            except Exception:
                pass
            
        self.client.index(indices[0]).update_settings({
            'displayedAttributes': ['title', 'author', 'date', 'link'],
            'searchableAttributes': ['title', 'author', 'date'],
            'rankingRules': ['typo', 'words', 'proximity', 'attribute', 
                             'wordsPosition', 'exactness', 'desc(timestamp)']})
        
        self.client.index(indices[1]).update_settings({
            'displayedAttributes': ['title', 'topics', 'type_of_act', 
                                     'start_date', 'end_date', 'status', 'link'],
            'searchableAttributes': ['title', 'topics', 'type_of_act', 'start_date', 
                                     'end_date', 'status'],
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
        results = []
        
        start_t = int(datetime.now().strftime("%s"))
        end_t = start_t
        
        while len(results) == 0 and end_t - start_t < 20*60:
            if 'twitter' in index:
                if 'query' in index:
                    results = self.search_query(query, count=pages, **params)
                else:
                    results = self.search_username(query, count=pages)
                
                if len(results) == 0:
                    print(datetime.now().strftime("%H:%M:%S:"),
                          'Twitter API limit reached. Retrying in 60s',
                          f'(Attempt {(end_t - start_t)//60}/20)')
                    sleep(60)
                    end_t = int(datetime.now().strftime("%s"))
                    continue
            else:
                results = self.search_many(query, pages, index, **params)

            update_id = db.add_documents(results)['updateId']
            
            while db.get_update_status(update_id)['status'] != 'processed':
                sleep(0.1)
            end_len = db.get_stats()['numberOfDocuments']
        
        return f"Found {len(results)} results. Added {end_len - start_len} new entries to {index} index"

    def build_ms_many(self, queries='default', pages=50, indices=None, rebuild=0,
                      **params):
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

        if indices is None:
            indices = self.indices
        elif not isinstance(indices, list):
            indices = [indices]
        
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
        return self.log

    def query_ms(self, query, index='eurlex', n=20):
        if index not in self.indices:
            return [{"Error": "index not recognised"}]
        else:
            return self.client.index(index).search(query, {'limit': n})['hits']
        
    def export_json(self, indices=None):
        if indices is None:
            indices = [idx['uid'] for idx in self.client.get_indexes()]
        elif not isinstance(indices, list):
            indices = indices.split(',')
        
        folder = join(dirname(dirname(__file__)), 'data.json')
        if not exists(folder):  # if folder doesn't exist
            os.makedirs(folder)  # create folder
        
        for index in indices:
            size = self.client.index(index).get_stats().get('numberOfDocuments', 0)
            export = self.client.index(index).get_documents({'limit':size})
            
            filepath = join(folder, f'{index}.json')
            
            with open(filepath, 'w') as file:
                json.dump(export, file)
            print(f'\nExported {size} entries from {index} to data.json/{index}.json')
    
    def import_json(self, replace=False):
        folder = join(dirname(dirname(__file__)), 'data.json')
        if not exists(folder):  # if folder doesn't exist
            print('No files found.')
            return
        
        files = os.listdir(folder)
        indices = [file.replace('.json', '') for file in files]
        if len(files) == 0:  # if no files
            print('No files found.')
            return
        
        for index, filename in zip(indices, files):
            try:
                self.client.create_index(index)
                print(f'Created {index} index')
            except Exception:
                pass
            
            db = self.client.index(index)

            if replace:
                update_id = db.delete_all_documents()['updateId']
                while db.get_update_status(update_id)['status'] != 'processed':
                    sleep(0.1)
                print(f'\nDeleted all documents from {index} index')
                
            filepath = join(folder, filename)
            with open(filepath, 'r') as file:
                json_ = json.load(file)
            print(f'\n{filename} contains {len(json_)} entries')
            
            start_len = db.get_stats()['numberOfDocuments']
            update_id = db.add_documents(json_)['updateId']
            while db.get_update_status(update_id)['status'] != 'processed':
                sleep(0.1)
                if db.get_update_status(update_id)['status'] == 'failed':
                    break
            
            end_len = db.get_stats()['numberOfDocuments']
            print(f'Imported {end_len - start_len} entries to {index}')


if __name__ == '__main__':
    if len(sys.argv) > 2:
        kwargs = {kwarg.split("=")[0]: kwarg.split("=")[1] for kwarg in sys.argv[2:]}
        getattr(Search(), sys.argv[1])(**kwargs)
    elif len(sys.argv) == 2:
        getattr(Search(), sys.argv[1])()

