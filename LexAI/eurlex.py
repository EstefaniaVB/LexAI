import requests
from bs4 import BeautifulSoup
import unicodedata

def search_one(query, page=1):
    url = "https://eur-lex.europa.eu/search.html"

    params = {
        "scope": "EURLEX",
        "text": query,
        "lang": "en",
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
        entry['title'] = unicodedata.normalize('NFKD', result.find('a', class_='title').text)
        entry['author'] = unicodedata.normalize('NFKD', result.find_all('div', class_='col-sm-6')[1].find_all('dd')[0].text)
        entry['date'] = unicodedata.normalize('NFKD', result.find_all('div', class_='col-sm-6')[1].find_all('dd')[1].text)
        entry['link'] = unicodedata.normalize('NFKD', result.find('a', class_='title')['name'])
        final_results.append(entry)
    return final_results

def search_many(query, pages=10):
    results = []
    for page in range(1, pages+1):
        results.append(query, page)
        
    return results

def store_many(query, pages):
    pass