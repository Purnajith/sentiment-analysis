from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import firestore
import base64
from google.cloud import pubsub_v1
import os

def convertToUnixEpoc(dateTimeData):
    return (dateTimeData - datetime(1970, 1, 1)).total_seconds()



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


    pass
