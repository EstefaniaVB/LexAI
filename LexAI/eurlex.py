import json
import re
import unicodedata
from os import path

import meilisearch
import requests
from bs4 import BeautifulSoup


class Search:
    
    def __init__(self, url='http://127.0.0.1:7700', key='',
                 indices=['eurlex', 'consultations']):
        
        ## run in terminal
        # curl -L https://install.meilisearch.com | sh
        # ./meilisearch
        
        self.client = meilisearch.Client(url, key)
        self.indices = indices
        for index in indices:
            try:
                self.client.create_index(index)
                print(f'Created {index} index')
            except:
                pass

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
        
        page_results = soup.find_all('div', class_='SearchResult')
        final_results = []
        
        if len(page_results) == 0 or len(r.history) >= 2:
            return
        
        for result in page_results:
            entry = {}
            
            celex = result.find_all('div', class_='col-sm-6')[0].find('dd')
            celex = result.find('p').text if celex is None else celex.text
            celex = re.sub(r'[^a-zA-Z0-9]', '', celex)
            
            title = result.find('a', class_='title')
            col2 = result.find_all('div', class_='col-sm-6')[1].find_all('dd')
            date = list(filter(lambda v: re.match("\d{2}/\d{2}/\d{4}", v.text), col2))[0]
            
            entry['id'] = unicodedata.normalize('NFKD', celex)
            entry['title'] = unicodedata.normalize('NFKD', title.text)
            entry['author'] = unicodedata.normalize('NFKD', col2[0].text)
            entry['date'] = unicodedata.normalize('NFKD', date.text[:10])
            entry['link'] = unicodedata.normalize('NFKD', title['name'])
            final_results.append(entry)

        return final_results
    
    def search_consultations(self, query, page=0, size=10, lang="EN"):
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

            consultations['id'] = initiative["id"]
            consultations['title'] = initiative["shortTitle"]
            consultations['type_of_act'] = initiative["foreseenActType"]
            # consultations['topics'] = initiative["topics"][0]["label"]
            consultations['status'] = initiative["currentStatuses"][0]["receivingFeedbackStatus"]
            consultations['start_date'] = initiative["currentStatuses"][0]["feedbackStartDate"]
            consultations['end_date'] = initiative["currentStatuses"][0]["feedbackEndDate"]
            
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
        start_len = self.client.index(index).get_stats()['numberOfDocuments']

        results = self.search_many(query, pages, index, **params)
        self.client.index(index).add_documents(results)
        end_len = self.client.index(index).get_stats()['numberOfDocuments']
        
        return f"Found {len(results)} results. Added {end_len - start_len} entries to {index} index"

    def build_ms_many(self, queries, pages, **params):
        for index in self.indices:
            start_len = self.client.index(index).get_stats()['numberOfDocuments']
            
            for query in queries:
                print(f"Searching {pages} pages for {query} in {index}. ")
                print(self.build_ms(query, pages, index, **params))
                
            end_len = self.client.index(index).get_stats()['numberOfDocuments']
            print(f"\nAdded {end_len - start_len} total entries to {index} index\n")

    def query_ms(self, query, index='eurlex', n=20):
        if index not in ['eurlex', 'consultations']:
            return "Error: index not recognised"
        else:
            return self.client.index(index).search(query, {'limit': n})['hits']
