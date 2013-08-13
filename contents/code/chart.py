# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from time import time, localtime, mktime
from math import floor, ceil


class Chart(Plasma.Label):
    def __init__(self, parent = None):
        Plasma.Label.__init__(self, parent)
        
        self._trades = []
        self._hourStep = 0
        self._right = 0
        self._currentTime = time()
        
        self.setMinimumSize(256, 256)

    def paint(self, painter, option, widget):
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing|QPainter.HighQualityAntialiasing)
            
        gridColor = painter.pen().color()
        gridColor.setAlpha(255)
        chartColor = QColor(0,255,0,255)
        pointColor = QColor(255,0,0,255)
        
        
        pen = QPen(gridColor)
        painter.setPen(pen)
            
        frame = option.rect
        center = frame.center()
        frame.setSize(frame.size() - QSize(100, 100))
        frame.moveCenter(center)
        painter.drawRect(frame)

        textSize = QFontMetrics(self.font()).size(Qt.TextSingleLine, '00:00')
        
        self._hourStep = textSize.width()*2
        self._right = frame.right()
        self._currentTime = time()
        
        x0, y0 = frame.left(), frame.top()
        x1, y1 = frame.right(), frame.bottom()
        height = frame.height()

        nTime = self._currentTime - (self._currentTime % 3600)
        
        # vertical lines
        while True:
            x = self.timeToX(nTime)
            if x <= x0:
                break
            painter.drawLine(x, y0, x, y0 + height)
            hour = str(localtime(nTime)[3]).zfill(2)
            painter.drawText(x - textSize.width()/2, y0 + height + textSize.height(), '%s:00' % hour)
            nTime -= 3600
            
        # minimax, trades
        trades = []
        first = True
        prev = None
        for timeStamp, value in self._trades:
            x = self.timeToX(timeStamp)
            if x0 < x < x1:
                if first:
                    minVal, maxVal = value, value
                    if prev:
                        dx = x - prev[0]
                        if dx > 0:
                            v = (value - prev[1])/dx*(x0 - prev[0]) + prev[1]
                            trades.append((x0, v))
                            minVal, maxVal = v, v
                    first = False
                else:
                    minVal = min(minVal, value)
                    maxVal = max(maxVal, value)
                trades.append((x, value))
            prev = x, value

        if trades and maxVal - minVal > 0:
            ext = (maxVal - minVal)*0.2
            minVal -= ext
            maxVal += ext
            coeff = (y1-y0)/(maxVal-minVal)
            
            # horizontal lines
            for value in range(int(minVal), int(ceil(maxVal))):
                y = y1 - (value-minVal)*coeff
                if y0 < y < y1:
                    painter.drawLine(x0, y, x1, y)
                    value = str(value)
                    textSize = QFontMetrics(self.font()).size(Qt.TextSingleLine, value)
                    painter.drawText(x0 - textSize.width() - 10, y, value)
            
            # chart
            coords = []
            for x, value in trades:
                coords.append(QPointF(x, y1 - (value-minVal)*coeff))
            if coords:
                pen = QPen(chartColor)
                painter.setPen(pen)
                painter.drawPolyline(*coords)
            
                pos = coords[-1]
                pen = QPen(pointColor)
                brush = QBrush(pointColor, Qt.SolidPattern)
                painter.setPen(pen)
                painter.setBrush(brush)
                painter.drawEllipse(pos, 2, 2)
                painter.drawPoint(pos)
                value = '%0.4f' % trades[-1][1]
                textSize = QFontMetrics(self.font()).size(Qt.TextSingleLine, value)
                
                painter.drawText(pos + QPointF(8, textSize.height()/2), value)
        
    def timeToX(self, time):
        return (self._right - (self._currentTime - time)/3600.0*self._hourStep) if self._hourStep else 0
    
    def dxToTime(self, dx):
        return (self._currentTime - dx*3600.0/self._hourStep) if self._hourStep else 0
    
    def getTimeInterval(self):
        return ((self._trades[-1][0] if self._trades else time() - self.dxToTime(self.geometry().width())), time())
        
    def addTrades(self, trades):
        self._trades.extend(trades)
        self.update()
        
    def clearTrades(self):
        self._trades = []
        self.update()
        
        
        