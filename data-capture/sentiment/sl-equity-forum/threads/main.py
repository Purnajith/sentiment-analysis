import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def extractContent(URL, container):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all("div", {"class" : container})
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
    if dataTimeAsString.find("at") > 0:
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

        dataTimeAsString = datetimeValue.strftime("%a %b %d, %Y %I:%M %p")
        pass

    finalDateTime = datetime.strptime(dataTimeAsString, "%a %b %d, %Y %I:%M %p")


    return (finalDateTime - datetime(1970, 1, 1)).total_seconds()


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
                pass
            elif infoTypeID == 2:
                equityStarts = userInfoList
                pass
            elif infoTypeID == 3:
                reputation = userInfoList
                pass
            elif infoTypeID == 4:
                joinDate = userInfoList
                pass
            elif infoTypeID == 5:
                location = userInfoList
                pass
            else:
                pass
            pass
        pass
    pass






def run(url):
    data = extractContent("https://srilankaequity.forumotion.com/t57943p200-east-west-properties-plc-east-n0000", "topic")

    for dataList in data:
        pass



    c = data[0].find_all("div", {"class" : 'post'})[0]

    head = c.find('div', class_='posthead') 
    #.find_all("div", {"class" : 'posthead'})[0] 
    print("id")
    print(head.get('id').partition('p')[2])

    print("dateTime")
    for contentData in head.find('h2'):
        if isinstance(contentData, str) and contentData != ' ':
            print(getUnixDateTime(contentData))
            pass
        pass

    body = c.find('div', class_='postbody') 

    

    print("entry")
    for entryContentList in body.find('div', class_='entry-content'):
        if entryContentList.text != '':
            for target_list in entryContentList:
                if target_list.text != '':
                    print(target_list.text)
                    pass
                pass
        pass

    footerData = c.find('div', class_='postfoot')

    likeContent  = footerData.find('div', class_='fa_like_div')
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
                print("like type")
                print(likeTypeID)
                if target_list.text != '':
                    print(target_list.text)
                    pass
                likeTypeID = 0
                pass
        pass

    #print(body.find('div', class_='entry-content').text)


    #print(c.prettify())

    #for target_list in data:
    #   for post in target_list.find_all("div", {"class" : 'post'}):
    #       print(post.prettify())
    #       pass
    #   pass

    #for threadLink in links:
        

    #    pass

    


    pass

run("https://srilankaequity.forumotion.com/t57943p200-east-west-properties-plc-east-n0000")



