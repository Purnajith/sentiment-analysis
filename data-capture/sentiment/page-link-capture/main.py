import requests
from bs4 import BeautifulSoup
import re
from google.cloud import pubsub_v1
import os


def extractContent(URL, container):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all('div', class_ = container)
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

def pushMessage(publisher, topic, linkList):
    
    topic = 'projects/{project_id}/topics/{topic}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
    topic=topic,  # Set this to something appropriate.
    )

    for link in linkList:
        publisher.publish(topic, data=link.encode("utf-8"))
        pass
    pass


def slEquityForum(publisher):
    URL = "https://srilankaequity.forumotion.com"
    content = extractContent(URL, "main-content")

    links = extractLinks(content, {"href" : lambda L: L and L.startswith('/t')}, "#", 0)    

    for threadLink in links:
        #send message to topic with link     
        link = URL + threadLink
        pushMessage(publisher, 'data-capture-sl-equity-forum-links', link)
        pass
    pass


def ftlk(publisher):
    URL = "http://www.ft.lk/"
    content = extractContent(URL, "container main")

    links = extractLinks(content, {"href" : lambda L: L and L.startswith('http://www.ft.lk/news/')}, "#", 0)
    links = links + extractLinks(content, {"href" : lambda L: L and L.startswith('http://www.ft.lk/business/')}, "#", 0)
    links = links + extractLinks(content, {"href" : lambda L: L and L.startswith('http://www.ft.lk/travel-tourism/')}, "#", 0)
    links = links + extractLinks(content, {"href" : lambda L: L and L.startswith('http://www.ft.lk/financial-services/')}, "#", 0)
    links = links + extractLinks(content, {"href" : lambda L: L and L.startswith('http://www.ft.lk/it-telecom-tec/')}, "#", 0)

    linkList = []

    for threadLink in links:
        if threadLink not in linkList:
            print(len(threadLink.split('/')))
            if len(threadLink.split('/')) > 5:
                linkList.append(threadLink)
                pass
            
    pass



    for link in linkList:
        #send message to topic with link     
        pushMessage(publisher, 'data-capture-ft-links', link)
        pass
    pass




def pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    publisher = pubsub_v1.PublisherClient()

    slEquityForum(publisher)

    ftlk(publisher)

    pass