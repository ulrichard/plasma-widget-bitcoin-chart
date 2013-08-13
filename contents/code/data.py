# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import urllib, json
from telnetlib import Telnet
from time import time
#from simple_thread import SimpleThread

TELNET_HOST, TELNET_PORT = 'bitcoincharts.com', 27007


class Data(QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        
        self._markets = []
        self._market = None
        self._telnet = None
        self._dataFlow = ''
        try:
            http = urllib.urlopen('http://bitcoincharts.com/t/markets.json')
            data = json.loads(http.read())
            for market in data:
                market = market.get('symbol')
                if market:
                    self._markets.append(market)
        except:
            self._markets = ["mtgoxUSD", "mtgoxCHF", "mtgoxEUR", "btcEUR"]
        self._telnet = Telnet(TELNET_HOST, TELNET_PORT)
                
    def init(self, market):
        if not market:
            return []
        self._market = market
        link = 'http://bitcoincharts.com/t/trades.csv?symbol=%s&start=%d&end=%d' % (self._market,
                                                                                    int(time() - 24*3600),
                                                                                    int(time()))
        http = urllib.urlopen(link)
        rows = http.read().split('\n')
        trades = []
        for row in rows:
            row = row.split(',')
            try:
                trades.append(tuple(map(float, row)[:2]))
            except:
                pass
            
        return trades
    
    def getData(self):

        trades = []
        try:
            self._dataFlow += self._telnet.read_very_eager()
            if self._dataFlow:
                print self._dataFlow
                rows = self._dataFlow.split('\r\n')
                self._dataFlow = rows[-1] or ''
                rows = rows[:-1]
                    
                for row in rows:
                    if row:
                        data = json.loads(row)
                        if data.get('symbol') == self._market:
                            trades.append((data.get('timestamp'), data.get('price')))
        except:
            print 'exception in data.getData()'
            pass
        return trades
        
    def markets(self):
        return self._markets
    
    def close(self):
        if self._telnet:
            self._telnet.close()

# test code
if __name__ == "__main__":
    print 'fetch the list of markets'
    data = Data()
    print data.markets()

    print 'fetch the information for mtgoxUSD'
    trades = data.init(u'mtgoxUSD')
    print trades

    print 'refreshing the data from telnet'
    for i in range(20):
        newdata = data.getData()
        if len(newdata) > 0:
            print newdata
            break
#        time.sleep(0.2)

    print 'done'

