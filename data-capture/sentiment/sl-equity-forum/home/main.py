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


def pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    publisher = pubsub_v1.PublisherClient()

    topic = 'projects/{project_id}/topics/{topic}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
    topic='sef-forum-links',  # Set this to something appropriate.
    )

    URL = "https://srilankaequity.forumotion.com"
    content = extractContent(URL, "main-content")

    links = extractLinks(content, {"href" : lambda L: L and L.startswith('/t')}, "#", 0)    

    for threadLink in links:
        #send message to topic with link     
        link = URL + threadLink
        publisher.publish(topic, data=link.encode("utf-8"))
        pass
    pass

pubsub(None, None)