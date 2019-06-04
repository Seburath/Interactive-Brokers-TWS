from ib.ext.Contract import Contract
from ib.opt          import ibConnection, message
from time            import sleep, strftime
import pandas as pd
import numpy as np


global hist
hist = []

def my_hist_data_handler(msg):
    print(msg)
    if "finished" in msg.date:
        print('disconnecting', con.disconnect())
        df = pd.DataFrame(index=np.arange(0, len(hist)), columns=('date', 'close' , 'volume'))
        for index, msg in enumerate(hist):
            df.loc[index,'date':'volume'] = msg.date, msg.close, msg.volume
        print(df )
    else:
        hist.append(msg)
         
def makeStkContract(contractTuple):
    newContract = Contract()
    newContract.m_symbol = contractTuple[0]
    newContract.m_secType = contractTuple[1]
    newContract.m_currency = contractTuple[2]
    newContract.m_exchange = contractTuple[3]
    return newContract

if __name__ == '__main__':
    
    con = ibConnection('127.0.0.1', 7496, 100)    
    con.register(my_hist_data_handler, message.historicalData)
    con.connect()
    sleep(1)
    contractTuple = (10, 'CASH', 'USD', 'IDEALPRO')
    stkContract = makeStkContract(contractTuple)
    endtime = strftime('%Y%m%d %H:%M:%S')   

    con.reqHistoricalData(36,stkContract,endtime,"3 D","30 mins","MIDPOINT",1,1)
    sleep(2)
    con.disconnect()
    
