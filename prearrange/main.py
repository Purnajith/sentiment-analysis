import base64
import firebase_admin
from firebase_admin import firestore
from datetime import datetime, timedelta
from textblob import TextBlob
import pandas as pd 
import time


def Average(lst): 
    return sum(lst) / len(lst) 

def getDocumentWithData(db, collection, ID):
    doc_ref = db.collection(collection).document(ID)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        print(u'No such document : ' + ID)
        return None

def convertToUnixEpoc(dateTimeData):
    return (dateTimeData - datetime(1970, 1, 1)).total_seconds()

def convertToUnixEpocWithMiliSeconds(epoch):
    return float(epoch * 1000)


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


def getCSEData(db, companyID, starttime, endTime):
    high=[]
    low=[]
    volume=[]
    cseDataCollection = db.collection(u'csedata').where(u'companyID', '==', int(companyID)).where(u'time', '>=', convertToUnixEpocWithMiliSeconds(starttime)).where(u'time', '<=', convertToUnixEpocWithMiliSeconds(endTime)).stream()
    
    for target_list in cseDataCollection:
        stockData = getDocumentWithData(db, 'csedata', target_list.id)

        if stockData:
            high.append(int(stockData['high']))
            low.append(int(stockData['low']))
            volume.append(int(stockData['volume']))
        pass

    if high and low and volume:
        return [Average(high), Average(low), Average(volume)]
    else :
        return None



def getSentimentFromPosts(db, keyWords, starttime, endTime):
    polarity=[]
    subjectivity=[]
    postDataCollection = db.collection(u'posts').where(u'fullArray', 'array_contains_any', keyWords).where(u'dateTime', '>=', starttime).where(u'dateTime', '<=', endTime).stream()

    for target_list in postDataCollection:
        postData = getDocumentWithData(db, 'posts', target_list.id)
        text = ''
        for word in postData['fullArray']:
            text = text + ' ' + word
            pass
        if text != '': 
            txtblb = TextBlob(text)
            if txtblb.sentiment.polarity > 0 or txtblb.sentiment.subjectivity > 0:
                polarity.append(txtblb.sentiment.polarity)
                subjectivity.append(txtblb.sentiment.subjectivity)
                pass
        pass

    if polarity and subjectivity :
        return [Average(polarity), Average(subjectivity)]
    else :
        return None
    

def getCombinedSentimentAnalysis(keywords, db, postStartTime, postEndTime):
    chunks = [keywords[x:x+10] for x in range(0, len(keywords), 10)]

    polarity = []
    subjectivity = []

    for target_list in chunks:
        data = getSentimentFromPosts(db, target_list, postStartTime, postEndTime)
        if data:
            polarity.append(data[0])
            subjectivity.append(data[1])    
            pass
        pass

    if polarity and subjectivity:
        return [Average(polarity), Average(subjectivity)]
    else : 
        return None


def storeData(db, data, id, cseStartTime, cseEndTime):
    key_format= id + "-"+ cseStartTime + "-"+ cseEndTime
    db.collection(u'arrangedData').document(key_format).set(data)
    pass


# create separation list
# select single record
# genarate sentiment for posts
# create cse records list by date 
# merge
# update db 
def preArrangeData(db, id):
    
    # create separation list
    separationList = getContentSeparationList()
    doc = getDocumentWithData(db, 'company',id)

    poststartDateList  = []
    postendDateList = []
    csestartDateList  = []
    cseendDateList = []
    polarity=[]
    subjectivity=[]
    high=[]
    low=[]
    volume=[]

    index = 0
    fullList = pd.DataFrame()
    for target_list in separationList:
        
        postStartTime = separationList[index - 1][0] if index > 0 else separationList[index][0]
        postEndTime = separationList[index][1]

        cseStartTime = target_list[0]
        cseEndTime = target_list[1]

        index = index + 1

        postSentimentList = getCombinedSentimentAnalysis(doc['keywords'], db, postStartTime, postEndTime)

        if postSentimentList:
            cseList = getCSEData(db, doc['id'], cseStartTime, cseEndTime)

            if cseList: 
                data = {
                    'companyID' : int(doc['id']),
                    'postStartRangeFull' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(postStartTime)),
                    'postEndRangeFull' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(postEndTime)),
                    'postStartRange' : postStartTime,
                    'postEndRange' : postEndTime,
                    'cseStartTimeFull' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cseStartTime)),
                    'cseEndTimeFull' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cseEndTime)),
                    'cseStartTime' : cseStartTime,
                    'cseEndTime' : cseEndTime,
                    'polarity' : postSentimentList[0],
                    'subjectivity' : postSentimentList[1],
                    'high' : cseList[0],
                    'low' : cseList[1],
                    'volume' : cseList[2]
                }
                

                poststartDateList.append(data['postStartRangeFull'])
                postendDateList.append(data['postEndRangeFull'])
                csestartDateList.append(data['cseStartTimeFull'])
                cseendDateList.append(data['cseEndTimeFull'])
                polarity.append(data['polarity'])
                subjectivity.append(data['subjectivity'])
                high.append(data['high'])
                low.append(data['low'])
                volume.append(data['volume'])

                storeData(db, data, str(int(doc['id'])), str(cseStartTime), str(cseEndTime))
                pass
            pass
        pass
    fullList['poststartDate'] = poststartDateList
    fullList['postendDate'] = postendDateList
    fullList['csestartDate'] = csestartDateList
    fullList['cseendDate'] = cseendDateList
    fullList['polarity'] = polarity
    fullList['subjectivity'] = subjectivity
    fullList['high'] = high
    fullList['low'] = low
    fullList['volume'] = volume


    print('=========================================================')
    print(doc['name'])
    print(fullList)
    print('=========================================================')
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

    #companyID = base64.b64decode(event['data']).decode('utf-8')


    # select single record
    # dialog 2 
    #doc = getDocumentWithData(db, 'company','iR01TsoyYnDwUwKXQSrG')
    # hnb gg3etvh7C90E8vAMYDCk 4
    #doc = getDocumentWithData(db, 'company','gg3etvh7C90E8vAMYDCk')
    # sampath wEILA31LJGLXgHAuF3IM 4
    #doc = getDocumentWithData(db, 'company','wEILA31LJGLXgHAuF3IM')
    # combank xuSaRuYgfHHLSD8og59x 5

    companyID = "ZFILlRgLyOWt6d7RAFrd"

    # get all current records 
    db = firebase_admin.firestore.client()

    try:

        #obselete use prediction/sentioment/main.py

        preArrangeData(db,companyID)
    except Exception as err:
        print(f'Error occurred: {err}')
        pass
    pass


# needs to move into a function  which accepts only a compnay id and date range 
pubsub(None, None)