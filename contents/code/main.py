#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on CPU and system viewer
# http://kde-look.org/content/show.php/CPU+and+System+Viewer?content=142178

#import urllib, json

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import KDialog
from PyQt4 import uic

from label_with_background import LabelWithBackground
from chart import Chart
from data import Data


class BtcChartPlasmoid(plasmascript.Applet):
    def __init__(self, parent, args=None):
        plasmascript.Applet.__init__(self, parent)
        
        self._market = None
        self._thread = None
        self._interval = 1
     
    def init(self):
        self.setHasConfigurationInterface(True)
        self.readConfig()
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)

        cfg = self.config()
        width, ok = cfg.readEntry('width', 256).toInt()
        height, ok = cfg.readEntry('height', 256).toInt()
        self.resize(width, height)
        
        self.applet.geometryChanged.connect(self.saveGeometry)
     
        self._theme = Plasma.Svg(self)
        self._theme.setImagePath('widgets/background')
        self.setBackgroundHints(Plasma.Applet.DefaultBackground)
     
        self._layout = QGraphicsGridLayout(self.applet)
        self.applet.setLayout(self._layout)

        self._chart = Chart(self.applet)
        self._chart.setZValue(1)
        self._layout.addItem(self._chart, 0, 0)
        
        self._data = Data(self)
        
        self.update()
        
    def update(self):
        self._timer = self.startTimer(self._interval*1000*60)
        self._chart.clearTrades()
        trades = self._data.init(self._market)
        self._chart.addTrades(trades)

    def timerEvent(self, event):
        self._chart.addTrades(self._data.getData())

    def createConfigurationInterface(self,  parent):
        parent.setButtons(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel | KDialog.Apply))

        self._generalConfig = QWidget()
        self._generalConfigUi = uic.loadUi(self.package().filePath('ui', 'general_config.ui'), self._generalConfig)
        parent.addPage(self._generalConfigUi,  'General',  self.icon(),  QString(),  False)

        self._generalConfigUi.intervalEdit.setValue(self._interval)
        if self._data:
            for market in self._data.markets():
                self._generalConfigUi.marketCombo.addItem(market)
                if market == self._market:
                    self._generalConfigUi.marketCombo.setCurrentIndex(self._generalConfigUi.marketCombo.count() - 1)
                    
        self.connect(parent, SIGNAL('applyClicked()'), self.configUpdated)
        self.connect(parent, SIGNAL('okClicked()'), self.configUpdated)

    def configUpdated(self):
        self._market = self._generalConfigUi.marketCombo.currentText()
        self._interval = self._generalConfigUi.intervalEdit.value()
        self.update()
        self._data.init(self._market)
        self.writeConfig()
        
    def readConfig(self):
        cfg = self.config()
        self._market = cfg.readEntry('market',  '').toString()
        self._interval, ok = cfg.readEntry('interval',  1).toInt()

    def writeConfig(self):
        cfg = self.config()
        cfg.writeEntry('market', self._market)
        cfg.writeEntry('interval', self._interval)
        self.emit(SIGNAL('configNeedsSaving()'))

    def saveGeometry(self):
        cfg = self.config()
        cfg.writeEntry('width', self.applet.geometry().width())
        cfg.writeEntry('height', self.applet.geometry().height())
        

def CreateApplet(parent):
    return BtcChartPlasmoid(parent)
