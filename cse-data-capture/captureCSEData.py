import requests
from requests.exceptions import HTTPError
from google.cloud import firestore

class CaptureCSEData  : 

    API_URL = "https://www.cse.lk/api/companyChartDataByStock?stockId={}&period=1"

    def getData(self, companyID):
        try:
            # map url
            url = self.API_URL.format(companyID)

            #get reposne
            resp = requests.post(url)

            # object format in { 'chartdata' : [ 'h' : = high price  'l' : low price 'q' : quatity/volume 'p' : purchased price 't' : time in unix epoch ] }
            jsonResponse = resp.json()

            return jsonResponse['chartData']
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        #print(resp.status_code)
        #print(resp.json())
        pass

    def storeData(self, companyID, list):
        # init firestore
        db = firestore.Client()
        for target_list in list:
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


    