import requests
from requests.exceptions import HTTPError
from google.cloud import firestore
import base64

    
def getData(companyID):
    API_URL = "https://www.cse.lk/api/companyChartDataByStock?stockId={}&period=1"
    
    try:
        # map url
        url = API_URL.format(companyID)

        #get reposne
        resp = requests.post(url)

        # object format in { 'chartdata' : [ 'h' : = high price  'l' : low price 'q' : quatity/volume 'p' : purchased price 't' : time in unix epoch ] }
        jsonResponse = resp.json()

        return jsonResponse['chartData']

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
        
    pass

def storeData(companyID, dataList):
    
    try:
        # init firestore
        db = firestore.Client()

        for target_list in dataList:
            data = {
                    "companyID" : companyID,
                    "high" : target_list['h'],
                    "low" : target_list['l'],
                    "time" : target_list['t'],
                    "volume" : target_list['q'],
                    "price" : target_list['p']
            }

            key_format = str(companyID) +"-"+ str(target_list['t'])

            db.collection(u'csedata').document(key_format).set(data)

            pass
        pass
    except Exception as err:
        print(f'Error occurred: {err}')
        pass

    pass


def run(companyID):
    print(companyID)
    data = getData(companyID)
    storeData(companyID, data)
    pass

#print("208 - #COMB.N0000")
#COMB.N0000
run(208)

#COMB.X0000
run(396)

#HNB.N0000
run(172)

#HNB.X0000
run(340)

#KHL.N0000
run(104)

#GHLL.N0000
run(116)

#DIAL.N0000
run(471)

