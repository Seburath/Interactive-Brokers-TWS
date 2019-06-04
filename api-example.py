from ib.opt import Connection, message, ibConnection
from ib.ext.Contract import Contract
from time import sleep, strftime
import pandas as pd
import numpy as np

global hist
hist = []

def my_hist_data_handler(msg):
    print(msg)
    # 當歷史資料跑完 = finished
    if "finished" in msg.date:
        # 確認結束連線
        print('disconnecting', con.disconnect())
        #  用 pandas 做好 hist 的 data frame 為 df, 設定要 call 回的資料行
        df = pd.DataFrame(index=np.arange(0, len(hist)), columns=('date', 'close' , 'volume'))
        # 開始將資料堆回 hist 
        for index, msg in enumerate(hist):
            df.loc[index,'date':'volume'] = msg.date, msg.open, msg.close
        # show 一下 df 確認無誤    
        print(df )
    else:
        # 如果還沒結束就繼續把 msg append 到 hist 上頭
        hist.append(msg)


def error_handler(msg):
    """Handles the capturing of error messages"""
    print("Server Error: %s" % msg)

def reply_handler(msg):
    """Handles of server replies"""
    print("Server Response: %s, %s" % (msg.typeName, msg))

def create_contract(symbol, sec_type, exch, prim_exch, curr):
    """Create a Contract object defining what will
    be purchased, at which exchange and in which currency.

    symbol - The ticker symbol for the contract
    sec_type - The security type for the contract ('STK' is 'stock')
    exch - The exchange to carry out the contract on
    prim_exch - The primary exchange to carry out the contract on
    curr - The currency in which to purchase the contract"""
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = sec_type
    contract.m_exchange = exch
    contract.m_primaryExch = prim_exch
    contract.m_currency = curr
    return contract


if __name__ == "__main__":
    # Connect to the Trader Workstation (TWS) running on the
    # usual port of 7496, with a clientId of 100
    # (The clientId is chosen by us and we will need 
    # separate IDs for both the execution connection and
    # market data connection)
    con = Connection.create(port=7496, clientId=100)
    con.connect()
    # Assign the error handling function defined above
    # to the TWS connection
    con.register(error_handler, 'Error')
    # Assign all of the server reply messages to the
    # reply_handler function defined above
    con.registerAll(reply_handler)

    # Create an order ID which is 'global' for this session. This
    # will need incrementing once new orders are submitted.
    order_id = 1

    #con.registerAll(watcher)
    # 註冊我們對回傳的 historicalData 要採取的 handler
    con.register(my_hist_data_handler, message.historicalData)
    # 開啟連線
    con.connect()
    # 設定要接回來的資料類型，在此為 EURUSD
    stkContract = create_contract('GOOG', 'STK', 'SMART', 'SMART', 'USD')
    # 設定接回來的合約格式
    # 設定接回來的資料的時間格式(不能改,是對Ib提供的固定格式)
    endtime = strftime('%Y%m%d %H:%M:%S')   
    # 開始連線拿資料, "5 D" = 拿 5 天 , "1 hour" = 拿每小時資料 , "MIDPOINT" = 拿的報價形式
    # 關於 各種 bar size 與 duration 能拿的對應資料其實很有限
    # 請見 : http://xavierib.github.io/twsapidocs/historical_limitations.html
    con.reqHistoricalData(1,stkContract,endtime,"3 W","15 mins","MIDPOINT",1,1)


    # Disconnect from TWS
    con.disconnect()

