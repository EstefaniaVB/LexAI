import json
import re
from unicodedata import normalize
from datetime import datetime
from os import path
from time import sleep, mktime
from LexAI.twittersearch import TwitterSearch

import meilisearch
import requests
from bs4 import BeautifulSoup


class Search(TwitterSearch):
    
    def __init__(self, url='http://127.0.0.1:7700', key='',
                 indices=['eurlex', 'consultations', 'twitter_query', 
                          'twitter_press', 'twitter_politicians']):
        
        ## run in terminal
        # curl -L https://install.meilisearch.com | sh
        # ./meilisearch
        
        super().__init__()
        self.client = meilisearch.Client(url, key)
        self.indices = indices
        for index in indices:
            try:
                self.client.create_index(index)
                print(f'Created {index} index')
            except:
                pass
            
        self.client.index(indices[0]).update_settings({
            'displayedAttributes': ['title', 'author', 'date', 'link'],
            'searchableAttributes': ['title', 'author', 'date'],
            'rankingRules': ['typo', 'words', 'proximity', 'attribute', 
                             'wordsPosition', 'exactness', 'desc(timestamp)']})
        
        self.client.index(indices[1]).update_settings({
            'displayedAttributes': ['title', 'topics', 'type_of_act', 
                                     'start_date', 'end_date', 'link'],
            'searchableAttributes': ['title', 'topics', 'type_of_act', 'start_date', 
                                     'end_date'],
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
        
        for initiative in content["initiativeResultDtoes"]:
            consultations = {}
            
            try:
                start_date = initiative["currentStatuses"][0]["feedbackStartDate"]
                end_date = initiative["currentStatuses"][0]["feedbackEndDate"]
            except IndexError:
                start_date = None
                end_date = None
                
            consultations['id'] = initiative["id"]
            consultations['title'] = initiative["shortTitle"]
            consultations['type_of_act'] = initiative["foreseenActType"]
            # consultations['topics'] = initiative["topics"][0]["label"]
            try:
                consultations['topics'] = initiative["topics"][0]["label"]
            except:
                consultations['topics'] = "Unknown"
            consultations['status'] = initiative["currentStatuses"][0]["receivingFeedbackStatus"]
            
            if start_date is not None:
                consultations['start_date'] = start_date[:10]
                consultations['start_timestamp'] = mktime(datetime.strptime(start_date, "%Y/%m/%d %H:%M:%S").timetuple())
            else:
                consultations['start_date'] = 'Unknown'
                consultations['start_timestamp'] = 0
                
            if end_date is not None:
                consultations['end_date'] = end_date[:10]
                consultations['end_timestamp'] = mktime(datetime.strptime(end_date, "%Y/%m/%d %H:%M:%S").timetuple())
            else:
                consultations['end_date'] = 'Unknown'
                consultations['end_timestamp'] = 0

            
            # links sometimes don't work, plz fix :)
            link_url = "https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/"
            title_link = consultations['title'].replace(" ","-")
            consultations['link']= f"{link_url}{consultations['id']}-{title_link}_en"
            
            final_results.append(consultations)
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
        
        while len(results) == 0:
            if 'twitter' in index:
                if 'query' in index:
                    results = self.search_query(query, count=pages, **params)
                else:
                    results = self.search_username(query, count=pages)
                
                if len(results) == 0:
                    print(datetime.now().strftime("%H:%M:%S") +
                          ': Twitter API limit reached. Retrying in 60s')
                    sleep(60)
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
            if rebuild:
                self.client.index(index).delete_all_documents()
                print(f'Deleted all documents from {index} index')
            
            self.log[index] = {}
            self.log[index]['rebuild'] = rebuild
            start_len = self.client.index(index).get_stats()['numberOfDocuments']
            
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
            
            end_len = self.client.index(index).get_stats()['numberOfDocuments']
            idx_result = f"Total: {end_len - start_len} new entries added to {index} index\n"
            
            self.log[index]['complete'] = idx_result
            print(idx_result)
        return self.log

    def query_ms(self, query, index='eurlex', n=20):
        if index not in self.indices:
            return [{"Error": "index not recognised"}]
        else:
            return self.client.index(index).search(query, {'limit': n})['hits']

