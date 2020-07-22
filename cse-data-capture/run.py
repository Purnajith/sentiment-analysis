import captureCSEData
from  datetime import datetime 

c = captureCSEData.CaptureCSEData()

data = c.getData(204)
c.storeData(204, data)