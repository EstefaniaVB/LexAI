import json
import re
import unicodedata

import meilisearch
import requests
from bs4 import BeautifulSoup

class Search:
    
    def __init__(self, url='http://127.0.0.1:7700', key=''):
        self.client = meilisearch.Client(url, key)

    def search_page(query, page=1, language='en'):
        url = "https://eur-lex.europa.eu/search.html"

        params = {
            "scope": "EURLEX",
            "text": query,
            "lang": language,
            "type": "quick",
            "DTS_DOM": "EU_LAW",
            "sortOne": "DD",
            "sortOneOrder": "desc",
            "page": page
        }

        html = requests.get(url, params=params).content
        soup = BeautifulSoup(html, 'html.parser')
        
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
            
            entry['id'] = unicodedata.normalize('NFKD', celex)
            entry['title'] = unicodedata.normalize('NFKD', title.text)
            entry['author'] = unicodedata.normalize('NFKD', col2[0].text)
            entry['date'] = unicodedata.normalize('NFKD', date.text[:10])
            entry['link'] = unicodedata.normalize('NFKD', title['name'])
            final_results.append(entry)

        return final_results

    def search_many(self, query, pages=10):
        results = []
        for page in range(1, pages+1):
            results.extend(self.search_page(query, page))
        return results

    def build_ms(self, query, pages=10, index='eurlex'):
        results = self.search_many(query, pages)
        self.client.index(index).add_documents(results)

    def query_ms(self, query, index='eurlex'):
        return self.client.index(index).search(query)['hits']

    def dump_ms(self, filename):
        uid = self.client.create_dump()['uid']
        print(f'Creating dump: {uid}.dump')
        return uid