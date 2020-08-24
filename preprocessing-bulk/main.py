import base64
import firebase_admin
from firebase_admin import firestore
import os
from google.cloud import pubsub_v1

def getDocumentWithData(db, ID):
    doc_ref = db.collection(u'posts').document(ID)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        print(u'No such document : ' + ID)
        return None

# select single record
# check if has sinhala 
# if has sinhala translate full text to new feild preprocessKey
# else copy the text to preprocessKey
# clean text
# tokenize
# remove stop words 
# update to stem 
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

    #dateTimeLast = base64.b64decode(event['data']).decode('utf-8')
    #dateTimeLast = 1593541800
    dateTimeLast = 1598293500.0
    # get all current records 
    db = firebase_admin.firestore.client()

    collection = db.collection(u'posts').where(u'dateTime', '>=', int(dateTimeLast)).order_by(u'dateTime').stream()

    publisher = pubsub_v1.PublisherClient()

    topic = 'projects/{project_id}/topics/{topic}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
    topic='preprocessing',  # Set this to something appropriate.
    )

    

    try:
        count = 1
        for doc in collection:
            data = getDocumentWithData(db, doc.id)
            print(str(count) + ' ' +doc.id + ' ' + str(data['dateTime']))
            count = count + 1
            #send message for pre processing
            publisher.publish(topic, data=doc.id.encode("utf-8"))
            
        pass
    except Exception as err:
        print(f'Error occurred: {err}')
        pass
    pass


pubsub(None,None)