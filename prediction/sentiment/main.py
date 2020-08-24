import firebase_admin
from firebase_admin import firestore 
from datetime import datetime, timedelta
import time
import base64

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

import pandas as pd

def average(lst): 
    return sum(lst) / len(lst) 

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

def checkKey(dict, key): 
    if key in dict.keys(): 
        return True 
    else: 
        return False

def getPostSentimentByPeriod(db, startDate, endDate, keyWordList):

    score = []
    magnitude = []
    polarity = []
    subjectivity = []
    # get unique Posts for Date
    docIDList = getPostIDsByKeyWord(db, startDate, endDate, keyWordList)

    for docID in docIDList:
        doc = getDocumentWithData(db, 'posts', docID)

        if doc and checkKey(doc, 'sentiment'):
            sentiment = doc['sentiment']
            if sentiment:
                if checkKey(sentiment, 'score') and  sentiment['score']:
                    score.append(sentiment['score'])
                    pass
                if checkKey(sentiment, 'magnitude') and  sentiment['magnitude']:
                    magnitude.append(sentiment['magnitude'])
                    pass
                if checkKey(sentiment, 'polarity') and  sentiment['polarity']:
                    polarity.append(sentiment['polarity'])
                    pass
                if checkKey(sentiment, 'subjectivity') and  sentiment['subjectivity']:
                    subjectivity.append(sentiment['subjectivity'])
                    pass
            pass
        pass
    pass

    scoreAverage = 0
    magnitudeAverage = 0
    polarityAverage = 0
    subjectivityAverage = 0

    if len(score) > 0:
        scoreAverage = average(score)
        pass
    if len(magnitude) > 0:
        magnitudeAverage = average(magnitude)
        pass
    if len(polarity) > 0:
        polarityAverage = average(polarity)
        pass
    if len(subjectivity) > 0:
        subjectivityAverage = average(subjectivity)
        pass

    if scoreAverage > 0 or magnitudeAverage > 0 or polarityAverage > 0 or subjectivityAverage > 0:
        return {
            "score" : scoreAverage,
            "magnitude" : magnitudeAverage,
            "polarity" : polarityAverage,
            "subjectivity" : subjectivityAverage
        }
    else :
        return None

    

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
        return {
            "high" : average(high),
            "low" : average(low),
            "volume" : average(volume),
        }
    else :
        return None


def setData(db, companyDoc):

    # create separation list
    separationList = getContentSeparationList()

    #get unique Key  words list for company
    companyKeyWords = getCompanyUniqueKeyWordList(companyDoc['keywords'])

    poststartDateList  = []
    postendDateList = []
    csestartDateList  = []
    cseendDateList = []
    score=[]
    magnitude=[]
    polarity = []
    subjectivity=[]
    high=[]
    low=[]
    volume=[]

    index = 0
    fullList = pd.DataFrame()
    for dateList in separationList:
        postStartTime = separationList[index - 1][0] if index > 0 else separationList[index][0]
        postEndTime = separationList[index][1]

        cseStartTime = dateList[0]
        cseEndTime = dateList[1]

        index = index + 1
        
        sentiment = getPostSentimentByPeriod(db, postStartTime, postEndTime, companyKeyWords)

        if sentiment:
            cseData = getCSEData(db, companyDoc['id'], cseStartTime, cseEndTime)

            if cseData :
                data = {
                    'companyID' : int(companyDoc['id']),
                    'postStartRangeFull' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(postStartTime)),
                    'postEndRangeFull' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(postEndTime)),
                    'postStartRange' : postStartTime,
                    'postEndRange' : postEndTime,
                    'cseStartTimeFull' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cseStartTime)),
                    'cseEndTimeFull' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cseEndTime)),
                    'cseStartTime' : cseStartTime,
                    'cseEndTime' : cseEndTime,
                    'score' : sentiment['score'],
                    'magnitude' : sentiment['magnitude'],
                    'polarity' : sentiment['polarity'],
                    'subjectivity' : sentiment['subjectivity'],
                    'high' : cseData['high'],
                    'low' : cseData['low'],
                    'volume' : cseData['volume'],
                }

                key_format= str(int(companyDoc['id'])) + "-"+ str(int(cseStartTime)) + "-"+ str(int(cseEndTime))
                db.collection(u'arrangedData').document(key_format).set(data)

                poststartDateList.append(data['postStartRangeFull'])
                postendDateList.append(data['postEndRangeFull'])
                csestartDateList.append(data['cseStartTimeFull'])
                cseendDateList.append(data['cseEndTimeFull'])
                score.append(data['score'])
                magnitude.append(data['magnitude'])
                polarity.append(data['polarity'])
                subjectivity.append(data['subjectivity'])
                high.append(data['high'])
                low.append(data['low'])
                volume.append(data['volume'])
            pass
        pass
    
    fullList['poststartDate'] = poststartDateList
    fullList['postendDate'] = postendDateList
    fullList['csestartDate'] = csestartDateList
    fullList['cseendDate'] = cseendDateList
    fullList['score'] = score
    fullList['magnitude'] = magnitude
    fullList['polarity'] = polarity
    fullList['subjectivity'] = subjectivity
    fullList['high'] = high
    fullList['low'] = low
    fullList['volume'] = volume


    print('=========================================================')
    print(companyDoc['name'])
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

    # get all current records 
    db = firebase_admin.firestore.client()

    #companyID = "G5cafrM2KPEVsJUag7dD" #JKH
    #companyID = "ZFILlRgLyOWt6d7RAFrd" #EXPO.N0000
    #companyID = "gg3etvh7C90E8vAMYDCk" #HNB.N0000
    #companyID = "iR01TsoyYnDwUwKXQSrG" #DIAL.N0000
    #companyID = "k8xL8W10kmm1Q6ZcN8jb" #VONE.N0000
    #companyID = "sTxEDZibOUZayDWcdJiv" #BIL.N0000
    #companyID = "swCENHeDqunTXOdHmES1" #EAST.N0000
    #companyID = "wEILA31LJGLXgHAuF3IM" #SAMP.N0000
    #companyID = "xuSaRuYgfHHLSD8og59x" #COMB.N0000
    companyID = "yQsjbu0Jsa60TydcK2j3" #AEL.N0000

    doc = getDocumentWithData(db, 'company', companyID)
        
    if doc :
        setData(db, doc)
    pass


pubsub(None, None)