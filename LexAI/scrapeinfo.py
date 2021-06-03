import re
from os.path import dirname, join

import pandas as pd
import requests
from bs4 import BeautifulSoup


def mep_info():
    xml = "https://www.europarl.europa.eu/meps/en/full-list/xml"
    base_url = "https://www.europarl.europa.eu/meps/en/"
    
    r_xml = requests.get(xml).content
    soup_xml = BeautifulSoup(r_xml, 'xml')
    meps = soup_xml('mep')
    all_data = {}
    for i, mep in enumerate(meps):
        if i % 50 == 0:
            print(f'Processed {i} MEPs')
        
        id = mep.find('id').text
        data_mep = {}
        data_mep['name'] = mep.find('fullName').text.title()
        data_mep['country'] = mep.find('country').text
        data_mep['eu_group'] = mep.find('politicalGroup').text
        data_mep['national_group'] = mep.find('nationalPoliticalGroup').text
        
        tags = {'Twitter': 'twitter.com/', 
                'Facebook': 'facebook.com/', 
                'Instagram': 'instagram.com/', 
                'LinkedIn': 'linkedin.com/in/', 
                'E-mail': '', 
                'Website': ''}
        
        mep_page = BeautifulSoup(requests.get(base_url + id).content, 'xml')
        for tag, base in tags.items():
            try:
                data = mep_page.find(attrs={'data-original-title': tag}).get('href', None)
                if tag == 'E-mail':
                    data_mep[tag.lower()] = data.replace('mailto:ue[dot]', '').replace('[at]', '@')[::-1] + '.eu'
                elif tag == 'Website':
                    data_mep[tag.lower()] = data
                else:
                    data = data.replace('https:', '').replace('http:', '').replace('//www.', '')
                    data = re.sub(r'\?.*', '', data).replace('@', '')
                    data_mep[tag.lower()] = data.replace(base, '').replace('/', '')
            except AttributeError:
                data_mep[tag.lower()] = None
        
        all_data[id] = data_mep
        
    df = pd.DataFrame.from_dict(all_data, orient='index')
    df.to_csv(join(dirname(__file__), 'data/meps.csv'))
    
    print(f'Done. Extracted info on {len(df)} MEPs.')
    
mep_info()
