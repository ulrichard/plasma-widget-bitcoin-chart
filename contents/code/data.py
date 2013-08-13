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
        
        http = urllib.urlopen('http://bitcoincharts.com/t/markets.json')
        data = json.loads(http.read())
        self._markets = []
        self._market = None
        self._telnet = None
        self._dataFlow = ''
        for market in data:
            market = market.get('symbol')
            if market:
                self._markets.append(market)
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
                rows = self._dataFlow.split('\r\n')
                self._dataFlow = rows[-1] or ''
                rows = rows[:-1]
                    
                for row in rows:
                    if row:
                        data = json.loads(row)
                        if data.get('symbol') == self._market:
                            trades.append((data.get('timestamp'), data.get('price')))
        except:
            pass
        return trades
        
    def markets(self):
        return self._markets
    
    def close(self):
        if self._telnet:
            self._telnet.close()

