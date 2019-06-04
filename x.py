from ib.opt import ibConnection, message
from ib.ext.Contract import Contract
from time import sleep, strftime
from datetime import datetime
import pandas as pd


class IBDataCache(object):

    def __init__(self, data_path='.', date_format='%Y%m%d %H:%M:%S', host='127.0.0.1', port=7497, client_id=None):
        self._data_path = data_path
        self._date_format = date_format
        self._reset_data()
        self._next_valid_id = 1

        self._conn = ibConnection(host, port, client_id)
        self._conn.enableLogging()
        # Register the response callback function and type of data to be returned
        self._conn.register(self._historical_data_handler, message.historicalData)
        self._conn.register(self._save_order_id, 'NextValidId')
        self._conn.connect()


    def _reset_data(self):
        self._df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'OpenInterest'])
        self._s = pd.Series()


    def _save_order_id(self, msg):
        self._next_valid_id = msg.orderId


    def _historical_data_handler(self, msg):
        """
            Define historical data handler for IB - this will populate our pandas data frame
        """

        print (msg.reqId, msg.date, msg.open, msg.close, msg.high, msg.low)
        if ('finished' in str(msg.date)) == False:
            self._s = ([datetime.strptime(msg.date, self._date_format),
                        msg.open, msg.high, msg.low, msg.close, msg.volume, 0])
            self._df.loc[len(self._df)] = self._s
    
        else:
            self._df.set_index('Date', inplace=True)


    def get_dataframe(self, sec_type, symbol, currency, exchange, endtime, duration, bar_size, what_to_show, use_rth):
        self._reset_data()

        # build filename
        filename = self._data_path + '/' + symbol + '_' + sec_type + '_' + exchange + '_' + currency + '_' + \
            endtime.replace(' ', '') + '_' + duration.replace(' ', '') + '_' + bar_size.replace(' ', '') + '_' + \
            what_to_show + '_' + str(use_rth) + '.csv'

        try:
            # check if we have this cached
            self._df = pd.read_csv(filename,
                         parse_dates=True,
                         index_col=0)
        except IOError:

            # Not cached. Download it.
            # Establish a Contract object and the params for the request
            req = Contract()
            req.m_secType = sec_type
            req.m_symbol = symbol
            req.m_currency = currency
            req.m_exchange = exchange

            self._conn.reqHistoricalData(self._next_valid_id, req, endtime, duration,
                                         bar_size, what_to_show, use_rth, 1)

            # Make sure the connection don't get disconnected prior the response data return
            sleep(5)
            self._conn.disconnect()

            # Cache dataframe to CSV
            self._df.to_csv(filename)

        return self._df


if __name__ == '__main__':

    date_format = '%Y%m%d %H:%M:%S'

    downloader_kwargs = dict(
        data_path='./data',
        date_format=date_format,
        host='127.0.0.1',
        port= 7496,
        client_id=100
    )
    downloader = IBDataCache(**downloader_kwargs)

    stock_kwargs = dict(
        sec_type='CASH',
        symbol='EUR',
        currency='USD',
        exchange='IDEALPRO',
        endtime=datetime(2018, 2, 14, 15, 59).strftime(date_format),
        duration='1 D',
        bar_size='1 min',
        what_to_show='TRADES',
        use_rth=1
    )

    df = downloader.get_dataframe(**stock_kwargs)
    print(df)


    stock_kwargs = dict(
        sec_type='STK',
        symbol='MSFT',
        currency='USD',
        exchange='SMART',
        endtime=datetime(2018, 2, 14, 15, 59).strftime(date_format),
        duration='1 D',
        bar_size='1 min',
        what_to_show='TRADES',
        use_rth=1
    )

    df = downloader.get_dataframe(**stock_kwargs)
    print(df)
