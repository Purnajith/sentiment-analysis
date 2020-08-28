import firebase_admin
from firebase_admin import firestore 
import pandas as pd
import numpy as np

def getDocumentWithData(db, collection, ID):
    doc_ref = db.collection(collection).document(ID)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        print(u'No such document : ' + ID)
        return None

def keywords():
    try:
        firebase_admin.initialize_app()
        pass
    except Exception as err:
        print(f'Error occurred: {err}')
        pass

    # get all current records 
    db = firebase_admin.firestore.client()
    
    companyCollection = db.collection(u'company').get()


    for companyDoc in companyCollection:
        doc = getDocumentWithData(db, 'company', companyDoc.id)   
        print(doc['id'])
        print(','.join(map(str,doc['keywords'])))
    pass

def loadData ():

    try:
        firebase_admin.initialize_app()
        pass
    except Exception as err:
        print(f'Error occurred: {err}')
        pass

    # get all current records 
    db = firebase_admin.firestore.client()

    dataCollection = db.collection(u'arrangedData').stream()
    output = pd.DataFrame()

    companyIDList = []

    for doc in dataCollection:  
        docData = getDocumentWithData(db, 'arrangedData', doc.id)

        if docData['score'] and docData['magnitude']:
            output = output.append(docData, ignore_index=True)
            if int(docData['companyID']) not in companyIDList:
                companyIDList.append(int(docData['companyID']))
        pass
    print(output)
    output.to_csv('./prediction/price/data2/arrangedData.csv', encoding='utf-8', index=False)
    #output.to_csv('./prediction/price/forcast/arrangedData.csv', encoding='utf-8', index=False)

    #train, validate, test = np.split(output, [int(.6*len(output)), int(.8*len(output))])

    #train.to_csv('./prediction/price/data2/arrangedData-train.csv', encoding='utf-8', index=False)
    #validate.to_csv('./prediction/price/data2/arrangedData-validate.csv', encoding='utf-8', index=False)
    #test.to_csv('./prediction/price/data2/arrangedData-test.csv', encoding='utf-8', index=False)



    trainframes = []
    validateframes = []
    testframes = []
    

    for companyID in companyIDList:
        filtere = output['companyID'] == companyID
        df = output[filtere]
        print(df)
        #df.to_csv('./prediction/price/data2/company/arrangedData-'+ str(companyID) +'.csv', encoding='utf-8', index=False)
    
        t, v, s = np.split(df, [int(.6*len(df)), int(.8*len(df))])
        trainframes.append(t)
        validateframes.append(v)
        testframes.append(s)

        #dftrain.to_csv('./prediction/price/data2/company/arrangedData-train-'+ str(companyID) +'.csv', encoding='utf-8', index=False)
        #dfvalidate.to_csv('./prediction/price/data2/company/arrangedData-validate-'+ str(companyID) +'.csv', encoding='utf-8', index=False)
        #dftest.to_csv('./prediction/price/data2/company/arrangedData-test-'+ str(companyID) +'.csv', encoding='utf-8', index=False)
        pass
        
        t = pd.concat(trainframes)
        v = pd.concat(validateframes)
        s = pd.concat(testframes)

        t.to_csv('./prediction/price/data2/arrangedData-train.csv', encoding='utf-8', index=False)
        v.to_csv('./prediction/price/data2/arrangedData-validate.csv', encoding='utf-8', index=False)
        s.to_csv('./prediction/price/data2/arrangedData-test.csv', encoding='utf-8', index=False)

    pass


#loadData()
keywords()