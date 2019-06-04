
from ib.ext.Contract import Contract
from ib.opt import ibConnection, message, Connection
from time import sleep, strftime



def my_hist_data_handler(msg):
    print(msg)
    print('asdas')
    if "finished" in msg.date:
        print('disconnecting', con.disconnect())
        df = pd.DataFrame(index=np.arange(0, len(hist)), columns=('date', 'close' , 'volume'))
        for index, msg in enumerate(hist):
            df.loc[index,'date':'volume'] = msg.date, msg.close, msg.volume
        print(df )
    else:
        hist.append(msg)



# print all messages from TWS
def watcher(msg):
    print(msg)

# show Bid and Ask quotes
def my_BidAsk(msg):
    if msg.field == 1:
        print('%s:%s: bid: %s' % (contractTuple[0],
                       contractTuple[6], msg.price))
    elif msg.field == 2:
        print('%s:%s: ask: %s' % (contractTuple[0], contractTuple[6], msg.price))

def makeStkContract(contractTuple):
    newContract = Contract()
    newContract.m_symbol = contractTuple[0]
    newContract.m_secType = contractTuple[1]
    newContract.m_exchange = contractTuple[2]
    newContract.m_currency = contractTuple[3]
    newContract.m_expiry = contractTuple[4]
    newContract.m_strike = contractTuple[5]
    newContract.m_right = contractTuple[6]
    print('Contract Values:%s,%s,%s,%s,%s,%s,%s:' % contractTuple)
    return newContract

if __name__ == '__main__':
    con = Connection.create(port=7496, clientId=100)
    

    con = ibConnection()
    con.registerAll(watcher)
    showBidAskOnly = True  # set False to see the raw messages
    if showBidAskOnly:
        con.unregister(watcher, message.tickSize, message.tickPrice,
                       message.tickString, message.tickOptionComputation)
        con.register(my_BidAsk, message.tickPrice)

    con.register(my_hist_data_handler, message.historicalData)

    con.connect()
    sleep(1)
    tickId = 1

    # Note: Option quotes will give an error if they aren't shown in TWS
    contractTuple = ('GOOG', 'STK', 'SMART', 'USD', '', 0.0, '')
    #contractTuple = ('QQQQ', 'OPT', 'SMART', 'USD', '20070921', 47.0, 'CALL')
    #contractTuple = ('ES', 'FUT', 'GLOBEX', 'USD', '200709', 0.0, '')
    #contractTuple = ('ES', 'FOP', 'GLOBEX', 'USD', '20070920', 1460.0, 'CALL')
    #contractTuple = ('EUR', 'CASH', 'IDEALPRO', 'USD', '', 0.0, '')
    stkContract = makeStkContract(contractTuple)

    print('* * * * REQUESTING MARKET DATA * * * *')
    con.reqMarketDataType(4)
    #con.reqMktData(tickId, stkContract, '', False)
    sleep(1)

   
    endtime = strftime('%Y%m%d %H:%M:%S')
    con.reqHistoricalData(1,stkContract,endtime,"3 W","15 mins","MIDPOINT",1,1)

    print('* * * * CANCELING MARKET DATA * * * *')
    #con.cancelMktData(tickId)
    sleep(0.1)
 
    con.disconnect()
    sleep(0.1)


