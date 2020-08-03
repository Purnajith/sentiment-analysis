import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import base64
import firebase_admin
from firebase_admin import firestore

def extractContent(URL, container):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all("div", {"class" : container})
    return results

def extractLinks(content, format, partition, extractContentNo):
    result = []
    for target_list in content:
        links = target_list.find_all("a", format)
        for link in links:
            # get link
            data = link['href']

            #  manipulate data
            if partition != "":
                data = data.partition(partition)[extractContentNo]
                pass
            
            # add to list
            result.append(data)
            pass
        pass
    return result

def pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    try:
        firebase_admin.initialize_app()
        pass
    except Exception as err:
        print(f'Error occurred: {err}')
        pass

    URL = "https://srilankaequity.forumotion.com/"
    content = extractContent(URL, "main-content")
    links = extractLinks(content, {"href" : lambda L: L and L.startswith('/t')}, "#", 0)    

    pass