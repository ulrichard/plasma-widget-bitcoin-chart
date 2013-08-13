# -*- coding: utf-8 -*-

# Based on CPU and system viewer
# http://kde-look.org/content/show.php/CPU+and+System+Viewer?content=142178

from PyKDE4.plasma import Plasma


class LabelWithBackground(Plasma.Label):

    def __init__(self, parent, args=None):
        Plasma.Label.__init__(self, parent)
        self._showBackground = 0

    def setShowBackground(self,  showBackground):
        self._showBackground = showBackground

    def paint(self,  painter,  option,  widget=None):
        # paint the background if we want to show it
        if (self._showBackground):
            contentsRect = self.contentsRect()
            painter.save()

            fm = QFontMetrics(painter.font())
            labelWidth = fm.width(' 100%')
            labelHeight = fm.height()

            textRectFactorHor= 1.1
            textRectFactorVer = 1.2
            textRectWidth = int(labelWidth * textRectFactorHor)
            textRectHeight = int(labelHeight * textRectFactorVer)

            textRect = QRect( contentsRect.left() + (contentsRect.width() - textRectWidth) / 2 ,  \
                              contentsRect.top() + (contentsRect.height() - textRectHeight) / 2,  \
                              textRectWidth,  \
                              textRectHeight)

            boxColor = QColor(Qt.white)
            boxColor.setAlpha(48)
            painter.setBrush(boxColor)
            painter.setPen(boxColor)

            roundProp = textRectWidth / textRectHeight
            roundRadius = 40.0
            painter.drawRoundedRect(textRect, float(roundRadius/roundProp), float(roundRadius),  Qt.RelativeSize)

            painter.restore()

        # and do the parent painting
        Plasma.Label.paint(self,  painter,  option,  widget)