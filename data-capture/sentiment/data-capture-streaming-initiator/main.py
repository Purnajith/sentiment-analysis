import firebase_admin
from firebase_admin import firestore
import base64
from google.cloud import pubsub_v1
import os

def getDocument(db, ID, collection):
    doc_ref = db.collection(collection).document(ID)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        print(u'No such document : ' + ID)
        return None


def pubMessage(publisher, text):
    
    topic = 'projects/{project_id}/topics/{topic}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
    topic='data-capture-text',  # Set this to something appropriate.
    )

    #send message for pre processing
    publisher.publish(topic, data=text.encode("utf-8"))

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
    
    db = firebase_admin.firestore.client()

    collection = db.collection(u'company').stream()

    
    keywords = []

    # create unique key word list
    for doc in collection:
        data = getDocument(db, doc.id, u'company')
        if data:
            for word in data['keywords']:
                if word.lower() not in keywords:
                    keywords.append(word.lower())    
                pass
            pass
        pass

    publisher = pubsub_v1.PublisherClient()

    # sent topic
    for word in keywords:
        pubMessage(publisher, word)
        pass
    pass