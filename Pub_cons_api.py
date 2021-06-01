from os import path
import requests

PAGES_TO_SCRAPE=2

query = "technology"
url = "https://ec.europa.eu/info/law/better-regulation/brpapi/searchInitiatives"
page=0
size=5
language="EN"


def get_consultations(query,page,size,language,url):
    response = requests.get(url, 
        params={'text': query, 'page': page,'size':size,'language':language}
        ).json()
    content= response["_embedded"]
    return content

def get_selected_info(content):
    consultations = []
    for n in range(size):    
        cons_id = content["initiativeResultDtoes"][n]["id"]
        title= content["initiativeResultDtoes"][n]["shortTitle"]
        type_of_act = content["initiativeResultDtoes"][n]["foreseenActType"]
        topics = content["initiativeResultDtoes"][n]["topics"][0]["label"]
        status = content["initiativeResultDtoes"][n]["currentStatuses"][0]["receivingFeedbackStatus"]
        start_date = content["initiativeResultDtoes"][n]["currentStatuses"][0]["feedbackStartDate"]
        end_date = content["initiativeResultDtoes"][n]["currentStatuses"][0]["feedbackEndDate"]
        title_link= title.replace(" ","-")
        link= f"https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/{cons_id}-{title_link}_en"
        consultations.append({'cons_id': cons_id, 'title': title,'topics': type_of_act,"type_of_act":type_of_act,"topics": topics, "status":status, "start_date":start_date,"end_date":end_date,"link":link})
    return consultations

def main():
    consultations_pages = []
    for page in range(PAGES_TO_SCRAPE):
        response = get_selected_info(get_consultations(query,page,size,language,url))
        if response:
            consultations_pages += response
        else:
            break
    return consultations_pages


if __name__ == '__main__':
    main()