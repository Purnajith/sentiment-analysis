import firebase_admin
from firebase_admin import firestore 
from datetime import datetime, timedelta
import time

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

def convertToUnixEpoc(dateTimeData):
    return (dateTimeData - datetime(1970, 1, 1)).total_seconds()

def convertToUnixEpocWithMiliSeconds(epoch):
    return float(epoch * 1000)

def getDocumentWithData(db, collection, ID):
    doc_ref = db.collection(collection).document(ID)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        print(u'No such document : ' + ID)
        return None

def getContentSeparationList():
    result = []

    startDate =  datetime(year=2020, month = 7,day = 1, hour=0, minute=0, second=0)
    endDate = startDate + timedelta(days=1)
    
    while endDate <= datetime.now()+ timedelta(days=1):
        rangeData = [convertToUnixEpoc(startDate), convertToUnixEpoc(endDate)]
        result.append(rangeData)
        startDate += timedelta(days=1)
        endDate += timedelta(days=1)
        pass

    return result


def getCompanyUniqueKeyWordList(keyWords):
    result = []
    for word in keyWords:
        if word not in result:            
            result.append(word)
        pass
    return result

def getPostIDsByKeyWord(db, startDate, endDate, keyWordList):
    result = []

    chunks = [keyWordList[x:x+10] for x in range(0, len(keyWordList), 10)]

    for chunk in chunks:
        postDataCollection = db.collection(u'posts').where(u'fullArray', 'array_contains_any', chunk).where(u'dateTime', '>=', startDate).where(u'dateTime', '<=', endDate).stream()

        for doc in postDataCollection:
            if doc.id not in result:
                result.append(doc.id)
                pass
            pass
        pass
    
    return result

def getPostSentimentByPeriod(db, startDate, endDate, keyWordList):

    score = []
    magnitiude = []
    magnitiude = []
    # get unique Posts for Date
    docIDList = getPostIDsByKeyWord(db, startDate, endDate, keyWordList)

    for docID in docIDList:
        doc = getDocumentWithData(db, 'posts', docID)

        pass


    pass


def storeData(companyDoc):

    # create separation list
    separationList = getContentSeparationList()

    #get unique Key  words list for company
    companyKeyWords = getCompanyUniqueKeyWordList(companyDoc['keywords'])


    index = 0
    for dateList in separationList:
        postStartTime = separationList[index - 1][0] if index > 0 else separationList[index][0]
        postEndTime = separationList[index][1]

        cseStartTime = dateList[0]
        cseEndTime = dateList[1]

        index = index + 1

        pass




    return getDocumentWithData(db, 'company',id)

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

    # get all current records 
    db = firebase_admin.firestore.client()

    companyDoc = getDocumentWithData(db, 'company', '')



    pass
