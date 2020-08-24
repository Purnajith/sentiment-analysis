import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import firestore
import base64
from google.cloud import pubsub_v1
import os

def convertToUnixEpoc(dateTimeData):
    return (dateTimeData - datetime(1970, 1, 1)).total_seconds()

def extractContent(URL, container):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all('div', class_ = container)
    return results

def storeEntry(url):

    db = firebase_admin.firestore.client()
    fullContent = extractContent(url, "lcol")

    for fullContentList in fullContent:

        titleContent = fullContentList.find_all('header', class_='inner-h')

        postTitle = None
        dateTime = None
        entryID = None

        for titleContentList in titleContent:
            for htag in titleContentList.find('h1'):
                if htag != '':
                    postTitle = htag
                pass
            pass

        contentList = fullContentList.find_all('header', class_='inner-content')
        for content in contentList:
            entry = content.text
        pass

        dateTimeText = fullContentList.find('span', class_='gtime').text

        if dateTimeText :
            dateTime = convertToUnixEpoc(datetime.strptime(dateTimeText, "%A, %d %B %Y %H:%M"))

        urlPart =  url.split('/')[-1]

        entryID = int(urlPart.replace("-",""))

        entryData = {
            "id" : entryID,
            "dateTime" : dateTime,
            "entry" : entry,
            "likeCount" : 0,
            "disLikeCount" : 0,
            "postTitle" : postTitle,
            "source" : "ft-lk"
        }

        postKeyFormat = str(entryID) + "-ft-lk" 

        db.collection(u'posts').document(postKeyFormat).set(entryData)

        publisher = pubsub_v1.PublisherClient()

        topic = 'projects/{project_id}/topics/{topic}'.format(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        topic='preprocessing',  # Set this to something appropriate.
        )

        #send message for pre processing
        publisher.publish(topic, data=postKeyFormat.encode("utf-8"))
        print(postKeyFormat)
        pass
    pass

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

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')

    print(str(pubsub_message))

    storeEntry(str(pubsub_message))

    pass
