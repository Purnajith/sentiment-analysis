import base64
import firebase_admin
from firebase_admin import firestore 
import re
from google.cloud import translate
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os


#clear the given text using regex 
def cleanText(text):
    stripped = text.strip()
    PATTERN = r'[,|.|?|$|#|!|&|*|@|(|)|~|:|;|<|>|/]'
    result = re.sub(PATTERN, r'', stripped)
    return result.lower().replace('"', '') 

# create a list of tokens for for the given text 
def tokenize(text):
    sentences = nltk.sent_tokenize(text)
    wordTokens = [nltk.word_tokenize(sentence) for sentence in sentences]
    return wordTokens

def getDocumentWithData(db, ID):
    doc_ref = db.collection(u'posts').document(ID)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        print(u'No such document : ' + ID)
        return None

# check if given string is english 
# we use encoding methods to identify if it passes anexception we it will be a sinhala text 
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def translateToEnglish(text):
    client = translate.TranslationServiceClient()

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats

    response = client.translate_text(
        parent='projects/{}'.format(os.getenv('GOOGLE_CLOUD_PROJECT')),
        contents=[text],
        mime_type="text/plain",  # mime types: text/plain, text/html
        source_language_code="si",
        target_language_code="en-US",
    )

    result = ''

    # Display the translation for each input text provided
    for translation in response.translations:
        result = result + translation.translated_text
        pass

    return result

def getEnglishText(text):
    # else copy the text to preprocessKey
    result = text
    # if has sinhala translate full text to new feild preprocessKey
    if not isEnglish(text):
        translatedText = translateToEnglish(text)
        if translatedText != '':
            result = translatedText
    return result

# removes stop words in the list using the passed stop word list 
def removeStopwords(stopwords, tokens):
    return [token for token in tokens if token not in stopwords]

# updates stem words according to passed stem list and returns the list of tokens 
def updateToStem(tokens):
    ps = PorterStemmer()
    return [ps.stem(token) for token in tokens]  

# convert back to a single array
def getSingleArray(arrayList):
    result = []
    for listData in arrayList:
        result = result + listData
        pass
    return  result

def preprocessDocument(doc, db, count):
    data = getDocumentWithData(db, doc.id)
    print(str(doc.id) + ' ' + str(data['dateTime'])+ ' ' + str(count))

    # check if has sinhala 
    textToProcess = getEnglishText(data['postTitle'])
    textToProcess = textToProcess + ' ' + getEnglishText(data['entry'])

    if textToProcess != '' : 
        # clean text
        textToProcess = cleanText(textToProcess)

        if textToProcess != '':
            # tokenize
            # https://stackoverflow.com/a/62209250
            # https://stackoverflow.com/a/58548615
            tokens = tokenize(textToProcess)

            # remove stop words
            stopwordList = set(stopwords.words('english'))
            stopWordsRemoved = [removeStopwords(stopwordList, tokenList) for tokenList in tokens]

            # update to stem
            stemWordUpdate = [updateToStem(tokenList) for tokenList in stopWordsRemoved]

            # update document
            db.collection(u'posts').document(doc.id).update({u'fullArray': getSingleArray(stopWordsRemoved)})
            db.collection(u'posts').document(doc.id).update({u'finalArray': getSingleArray(stemWordUpdate)})
            db.collection(u'posts').document(doc.id).update({u'preprocessed': True})
            pass
        pass
    pass
    pass

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

    dateTimeLast = base64.b64decode(event['data']).decode('utf-8')

    # get all current records 
    db = firebase_admin.firestore.client()

    collection = db.collection(u'posts').where(u'dateTime', '>', int(dateTimeLast)).order_by(u'dateTime').limit(100).stream()

    try:
        count = 1
        for doc in collection:
            preprocessDocument(doc, db, count)
            count = count + 1
        pass
    except Exception as err:
        print(f'Error occurred: {err}')
        pass
    pass


