import pandas as pd
import numpy as np
from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from time import sleep, strftime


global hist

def my_hist_data_handler(msg):
    if "finished" in msg.date:
        print('disconnecting', con.disconnect())
        df = pd.DataFrame(index=np.arange(0, len(hist)), columns=('date', 'close' , 'volume'))
        for index, msg in enumerate(hist):
            df.loc[index,'date':'volume'] = msg.date, msg.close, msg.volume
    else:
        hist.append(msg)
         
def makeContract(contractTuple):
    newContract = Contract()
    newContract.m_symbol = contractTuple[0]
    newContract.m_secType = contractTuple[1]
    newContract.m_exchange = contractTuple[2]
    newContract.m_currency = contractTuple[3]
    return newContract

def pull_data(con, contractTuple, time_range, time_interval):
    con.register(my_hist_data_handler, message.historicalData)
    con.connect()
    sleep(1)

    #con.reqMarketDataType(4)
    endtime = strftime('%Y%m%d %H:%M:%S')   
    contract = makeContract(contractTuple)
    con.reqHistoricalData(1,contract,endtime,time_range, time_interval,"MIDPOINT",1,1)
    sleep(1)
    con.disconnect()

def detect_decrese(var_to_analyze):
    higher = hist[0]
    droped = False
    for price in hist:
        if price.close > higher.close:
            higher = price

        var = (higher.close - price.close) / higher.close
        if not droped and var >= var_to_analyze:
            droped = True
            drop = price
            print('from ', higher.date)
            print('drop on ', drop.date)
        
        if droped and price.close >= higher.close:
            droped = False
            print('recovered at ', price.date)
            drop = 0

       
if __name__ == '__main__':
    
    var_to_analyze = 0.0012
    time_range = "3 W"
    time_interval = "15 mins"
    con = ibConnection('127.0.0.1', 7496, 100)    
    tuples = [('EUR', 'CASH', 'IDEALPRO', 'USD'),
              ('EUR', 'CASH', 'IDEALPRO', 'USD'), 
              ('EUR', 'CASH', 'IDEALPRO', 'USD')]
 
    for contractTuple in tuples:
        hist=[]
        print('/' * 50)
        print(contractTuple)
        pull_data(con, contractTuple, time_range, time_interval)
        print('/' * 50)
        detect_decrese(var_to_analyze)
