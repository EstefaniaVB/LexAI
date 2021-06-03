from os import path
import requests

PAGES_TO_SCRAPE=3
query = "agriculture"

def get_consultations(query,page,size,language,url):
    response = requests.get(url, 
        params={'text': query, 'page': page,'size':size,'language':language}
        ).json()
    try:
        content= response["_embedded"]
        return content
    except:
        return None

def get_selected_info(content):
    if not content:
        return None
    consultations = []
    for iniciative in content["initiativeResultDtoes"]:
        cons_id = iniciative["id"]
        title= iniciative["shortTitle"]
        type_of_act = iniciative["foreseenActType"]
        status = iniciative["currentStatuses"][0]["receivingFeedbackStatus"]
        start_date = iniciative["currentStatuses"][0]["feedbackStartDate"]
        end_date = iniciative["currentStatuses"][0]["feedbackEndDate"]
        title_link= title.replace(" ","-")
        link= f"https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/{cons_id}-{title_link}_en"
        try:
            topics= iniciative["topics"][0]["label"]
        except:
            topics= ""
        consultations.append({'cons_id': cons_id, 'title': title,'topics': type_of_act,"type_of_act":type_of_act,"topics": topics, "status":status, "start_date":start_date,"end_date":end_date,"link":link})
    return consultations

def main(PAGES_TO_SCRAPE,query):
    url = "https://ec.europa.eu/info/law/better-regulation/brpapi/searchInitiatives"
    size=20
    language="EN"
    page = 0 
    consultations_pages = []
    for page in range(PAGES_TO_SCRAPE):
        
        response = get_selected_info(get_consultations(query,page,size,language,url))
        if response:
            consultations_pages += response
        else:
            break
    return consultations_pages


if __name__ == '__main__':
    result = main(PAGES_TO_SCRAPE,query)
    print(result)