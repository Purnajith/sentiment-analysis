import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import firestore

def convertToUnixEpoc(dateTimeData):
    return (dateTimeData - datetime(1970, 1, 1)).total_seconds()

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



def getUnixDateTime(contentData):
    dataTimeAsString = contentData.rstrip().lstrip()

    # convert to common date time format
    if dataTimeAsString.find(" at ") > 0:
        splitDate = dataTimeAsString.split('at')
                
        dateStringPart = splitDate[0].rstrip().lstrip()
        timeStringPart = splitDate[1].rstrip().lstrip()

        
        datetimeValue = datetime.now()
        if dateStringPart == "Yesterday" :
            # change date time to yesturday date
            datetimeValue = datetime.now() - timedelta(days=1)
            pass
                
        timeTemp = datetime.strptime(timeStringPart, "%I:%M %p")
        datetimeValue = datetimeValue.replace(hour=timeTemp.hour)
        datetimeValue = datetimeValue.replace(minute=timeTemp.minute)

        dataTimeAsString = datetimeValue.strftime("on %a %b %d, %Y %I:%M %p")
        pass

    finalDateTime = datetime.strptime(dataTimeAsString, "on %a %b %d, %Y %I:%M %p")


    return convertToUnixEpoc(finalDateTime)


def getUserInfo(body):
    
    userName = body.find('h4', class_='username').text
    role = None
    posts = None
    equityStarts = None
    reputation = None
    joinDate = None
    location = None

    #print("user")
    #print(body.find('h4', class_='username').text)
    
    for userBasicInfoList in body.find('div', class_='user-basic-info'):
        if userBasicInfoList.find('.//*') is not None:
            role = userBasicInfoList
            pass
        pass

    
    infoTypeID = 0
    for userInfoList in body.find('div', class_='user-info'):
        #<span class="label">
        #    <span style="color:#536482;">
        #        Posts
        #   </span>
        #    :
        #</span>
        #26
        #<br/>

        if userInfoList.find('.//*') is None:
            for innerList in userInfoList:
                for content in innerList:
                     if content == 'Posts':
                         infoTypeID = 1
                         pass
                     elif content == 'Equity Stars' :
                         infoTypeID = 2
                         pass
                     elif content == 'Reputation' :
                         infoTypeID = 3
                         pass
                     elif content == 'Join date' :
                         infoTypeID = 4
                         pass
                     elif content == 'Location' :
                         infoTypeID = 5
                         pass
                     else:
                         pass
                     pass
                pass
            pass
        else :
            if infoTypeID == 1:
                posts = userInfoList
                infoTypeID = 0
                pass
            elif infoTypeID == 2:
                equityStarts = userInfoList
                infoTypeID = 0
                pass
            elif infoTypeID == 3:
                reputation = userInfoList
                infoTypeID = 0
                pass
            elif infoTypeID == 4:
                joinDate = userInfoList
                infoTypeID = 0
                pass
            elif infoTypeID == 5:
                location = userInfoList
                infoTypeID = 0
            else:
                pass
            pass
        pass
    pass

    

    return {
        "userName" : userName,
        "role" : role,
        "posts" : posts,
        "equityStarts" : equityStarts,
        "reputation" : reputation,
        "joinDate" : convertToUnixEpoc(datetime.strptime(joinDate, "%Y-%m-%d")),
        "location" : location
    }

def getEntry(body):
    result = ''
    for entryContentList in body.find('div', class_='entry-content'):
        if entryContentList.text != '':
            for target_list in entryContentList:
                if target_list.text != '':
                    result = target_list.text
                    pass
                pass
            pass
        pass
    pass
    return result

def getFooterContent(footer):
    likeCount = 0
    disLikeCount = 0

    likeContent  = footer.find('div', class_='fa_like_div')
    #likeContent.find('span', class_='rep-nb')
    likeTypeID = 0
    for contentList in likeContent:
        for target_list in contentList:
            if target_list.text != '':
                if  target_list.text == 'Like' :
                    likeTypeID = 1
                    pass
                elif target_list.text == 'Dislike' : 
                    likeTypeID = 2
                    pass
                else :
                    pass
            pass
            
            if likeTypeID > 0 :
                if target_list.text != '' and isinstance(target_list.text, int):
                    if likeTypeID == 1:
                        likeCount = int(target_list.text)
                    elif likeTypeID == 2:
                        disLikeCount = int(target_list.text)
                    pass
                    likeTypeID = 0
                pass

        pass
    return {
        "likeCount" : likeCount,
        "disLikeCount" : disLikeCount
    }


def storeEntry(dataList, postTitle, db): 
    head = dataList.find('div', class_='posthead')
    body = dataList.find('div', class_='postbody')
    foot = dataList.find('div', class_='postfoot')

    # id
    entryID = head.get('id').partition('p')[2]
    #date time
    dateTime = 0
    #user info
    userInfo = None
    #entry
    entry = None

    for contentData in head.find('h2'):
        if isinstance(contentData, str) and contentData != ' ':
            dateTime = getUnixDateTime(contentData)
            pass
        pass

    # only pick records after 2020 07 01 00:00:00
    if dateTime > float(1593541800): 
        userInfo = getUserInfo(body)
        entry =  getEntry(body)
        footer  = getFooterContent(foot)

        userKeyFormat = userInfo['userName'] + "-sef" 
        postKeyFormat = entryID + "-sef" 

        entryData = {
            "id" : entryID,
            "dateTime" : dateTime,
            "entry" : entry,
            "likeCount" : footer['likeCount'],
            "disLikeCount" : footer['disLikeCount'],
            "postTitle" : postTitle,
            "userName" : userInfo['userName'],
            "source" : "sl-equity-form",
            "userID" : userKeyFormat
        }

        db.collection(u'users').document(userKeyFormat).set(userInfo)
        db.collection(u'posts').document(postKeyFormat).set(entryData)

        pass
    pass


def run(url):
    db = firebase_admin.firestore.client()
    fullContent = extractContent(url, "main paged")

    for fullContentList in fullContent:

        titleContent = fullContentList.find_all('div', class_='paged-head')

        postTitle = None

        for titleContentList in titleContent:
            for htag in titleContentList.find('h1'):
                if htag != '':
                    postTitle = htag
                pass
            pass

        topicContent = fullContentList.find_all('div', class_='topic')

        for topicContentList in topicContent:
            data = topicContentList.find_all('div', class_='post')

            for dataList in data:
                try:
                    storeEntry(dataList, postTitle, db)
                    pass
                except Exception as err:
                    print(f'Error occurred: {err}')
                pass
            pass
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

    URL = "https://srilankaequity.forumotion.com/"
    content = extractContent(URL, "main-content")
    links = extractLinks(content, {"href" : lambda L: L and L.startswith('/t')}, "#", 0)    

    for threadLink in links:
        run(URL + threadLink)
        pass
    pass
