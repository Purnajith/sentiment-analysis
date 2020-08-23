from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import firestore
import base64
from google.cloud import pubsub_v1
import os
import tweepy

def convertToUnixEpoc(dateTimeData):
    return (dateTimeData - datetime(1970, 1, 1)).total_seconds()

def getTweets(keyWord):
    auth = auth = tweepy.AppAuthHandler(os.getenv('twitter_consumer_key') , os.getenv('twitter_consumer_secret'))
    api = tweepy.API(auth, retry_count= 3, wait_on_rate_limit=True)

    ##geo = "80.66217120847085,7.878660200000001,300km"
    ##[80.66217120847085, 7.878660200000001]
    #  twitter sri lnaka coodinates
    geo = "7.878660200000001,80.66217120847085,200km"

    return tweepy.Cursor(api.search, 
                                q=keyWord, 
                                geocode = geo,
                                include_entities=True, tweet_mode='extended').items()

        
def getUserInfo(user):
    return {
        "userName" : user.screen_name,
        "posts" : user.statuses_count,
        "joinDate" : convertToUnixEpoc(user.created_at),        
        "location" : user.location,
        "followersCount" : user.followers_count,
        "id" : user.id
    }

def storeData(tweet, db):
    userInfo = getUserInfo(tweet.user)
    userKeyFormat = userInfo['userName'] + "-twitter" 
    postKeyFormat = str(tweet.id) + "-twitter"

    entry = ""
    try:
        entry = tweet.retweeted_status.full_text
    except AttributeError:  # Not a Retweet
        entry = tweet.full_text

    entryData = {
            "id" : tweet.id,
            "dateTime" : convertToUnixEpoc(tweet.created_at),
            "entry" : entry,
            "likeCount" : tweet.retweet_count + tweet.favorite_count,
            "disLikeCount" : 0,
            "postTitle" : "",
            "userName" : userInfo['userName'],
            "source" : "twitter",
            "userID" : userKeyFormat
    }

    db.collection(u'users').document(userKeyFormat).set(userInfo)
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


def run(keyword):
    
    try:
        firebase_admin.initialize_app()
        pass
    except Exception as err:
        print(f'Error occurred: {err}')
        pass


    db = firebase_admin.firestore.client()

    for tweet in getTweets(keyword):
        storeData(tweet, db)
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

    if pubsub_message != '':
        print(pubsub_message)
        run(pubsub_message)

    pass
