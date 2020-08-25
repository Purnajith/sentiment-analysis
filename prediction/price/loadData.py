import firebase_admin
from firebase_admin import firestore 
import pandas as pd

def getDocumentWithData(db, collection, ID):
    doc_ref = db.collection(collection).document(ID)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        print(u'No such document : ' + ID)
        return None

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
        output = output.append(docData, ignore_index=True)
        if int(docData['companyID']) not in companyIDList:
            companyIDList.append(int(docData['companyID']))
        pass
    print(output)
    output.to_csv('./prediction/price/arrangedData.csv', encoding='utf-8', index=False)

    for companyID in companyIDList:
        filtere = output['companyID'] == companyID
        df = output[filtere]
        print(df)
        df.to_csv('./prediction/price/arrangedData-'+ str(companyID) +'.csv', encoding='utf-8', index=False)
        pass
    pass


loadData()