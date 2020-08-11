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
    PATTERN = r'[,|.|?|$|#|!|&|*|%|@|(|)|~|^0-9]'
    result = re.sub(PATTERN, r'', stripped)
    return result.lower().replace('"', '') 

# create a list of tokens for for the given text 
def tokenize(text):
    sentences = nltk.sent_tokenize(text)
    wordTokens = [nltk.word_tokenize(sentence) for sentence in sentences]
    return wordTokens

def getDocument(db, ID):
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

    print(os.getenv('GOOGLE_CLOUD_PROJECT'))

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
    result = []
    ps = PorterStemmer()
    for token in tokens:
        row = ps.stem(token)
        if not row.empty :
            result.append(row["stem"].values.tolist()[0])
        else :
            result.append(token)
    return result




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

    # get all current records 
    db = firebase_admin.firestore.client()

    collection = db.collection(u'posts').limit(1).stream()

    for doc in collection:
        # select single record
        #data = getDocument(db, doc.id)
        data = getDocument(db, '365185-sef')

        print(data['postTitle'])
        print(data['entry'])

        print(os.environ['GOOGLE_CLOUD_PROJECT'])

        # check if has sinhala 
        textToProcess = getEnglishText(data['postTitle'])
        textToProcess = textToProcess + ' ' + getEnglishText(data['entry'])

        if textToProcess != '' : 
            # clean text
            textToProcess = cleanText(textToProcess)
            print(textToProcess)

            if textToProcess != '':
                # tokenize
                # https://stackoverflow.com/a/62209250
                # https://stackoverflow.com/a/58548615
                tokens = tokenize(textToProcess)
                print(tokens)

                print(os.environ['NLTK_DATA'])

                # remove stop words
                stopwordList = stopwords.words('english')
                stopWordsRemoved = removeStopwords(stopwordList, tokens)
                print(stopWordsRemoved)

                # update to stem
                stemWordUpdate = updateToStem(stopWordsRemoved)
                print(stemWordUpdate)
                
                pass
            pass
        pass
    #pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    #run(int(pubsub_message))

    pass



pubsub(None, None)