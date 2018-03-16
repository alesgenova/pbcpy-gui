#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

This example shows a tooltip on 
a window and a button.

Author: Jan Bodnar
Website: zetcode.com 
Last edited: August 2017
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QToolTip, QAction,
    QPushButton, QApplication, QMainWindow, QSlider, QHBoxLayout, QVBoxLayout, QLCDNumber)
from PyQt5.QtGui import QFont, QIcon


class PbcPyQt(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.openedFiles = []
        
        self.initUI()
        
        
    def initUI(self):
        
        self.initMenuBar()
        self.initStatusBar()
        self.initMainArea()

        self.setGeometry(500, 500, 600, 400)
        self.setWindowTitle('PbcPy-Qt')    
        self.show()

    def initMenuBar(self):
        menubar = self.menuBar()
        toolbar = self.addToolBar("Menu")

        fileMenu = menubar.addMenu('&File')
        fileOpenAct = QAction(QIcon.fromTheme('document-open'), "&Open", self)
        fileOpenAct.triggered.connect(self.printMsg)
        fileOpenAct.setShortcut('Ctrl+O')

        fileCloseAct = QAction(QIcon.fromTheme('window-close'), "&Close", self)
        fileCloseAct.setShortcut('Ctrl+W')

        fileQuitAct = QAction(QIcon.fromTheme('application-exit'), "&Quit", self)
        fileQuitAct.setShortcut('Ctrl+Q')
        fileQuitAct.triggered.connect(QApplication.instance().quit)

        fileMenu.addActions([fileOpenAct,fileCloseAct,fileQuitAct])
        toolbar.addActions([fileOpenAct,fileCloseAct,fileQuitAct])


    def initStatusBar(self):
        self.statusbar = self.statusBar()
        isoSlider = QSlider(Qt.Horizontal, self.statusbar)
        #isoSlider.setRange()
        isoSlider.setRange(-5, -1)
        isoSlider.valueChanged.connect(self.onIsoChange, isoSlider.value())
        #self.statusbar.showMessage('Ready')

    def printMsg(self):
        print("I have been clicked")

    def onIsoChange(self, n):
        print("I have changed {}".format(10.**n))

    def initMainArea(self):
        pass
        # vbox = QVBoxLayout()
        # lcd = QLCDNumber(self)
        # isoSlider = QSlider(Qt.Horizontal, self)
        # vbox.addWidget(lcd)
        # vbox.addWidget(isoSlider)
        # self.setLayout(vbox)

    def addFile(self, filename):
        pass

    def closeFiles(self):
        self.closedFiles = []
        pass
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ui = PbcPyQt()
    sys.exit(app.exec_())
