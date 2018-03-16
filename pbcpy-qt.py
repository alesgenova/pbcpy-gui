#!/usr/bin/python3

import sys
from collections import OrderedDict

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QToolTip, QAction, QTextEdit, QFileDialog,
    QPushButton, QApplication, QMainWindow, QSlider, QHBoxLayout, QVBoxLayout, QLCDNumber)
from PyQt5.QtGui import QFont, QIcon

import vtkField
from pbcpy.formats.qepp import PP


class PbcPyQt(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.openedFiles = {}
        self.isoValue = -1
        self.initUI()
        
        
    def initUI(self):

        self.setAcceptDrops(True)

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
        fileOpenAct.triggered.connect(self.fileDialog)
        fileOpenAct.setShortcut('Ctrl+O')

        fileCloseAct = QAction(QIcon.fromTheme('window-close'), "&Close", self)
        fileCloseAct.triggered.connect(self.closeFiles)
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
        self.isoValue = 10.**n
        for key, item in self.openedFiles.items():
            item["contour"].SetValue(0,self.isoValue)
        self.vtkWidget.GetRenderWindow().Render()
        #print("I have changed {}".format(10.**n))

    def fileDialog(self):
        fname = QFileDialog.getOpenFileName(self, "", "", "Quantum Espresso (*.pp)")

        if fname[0]:
            self.processFile(fname[0])


    def processFile(self, filename):
        if filename in self.openedFiles:
            return
        i = len(self.openedFiles)
        self.openedFiles[filename] = {}

        system = PP(filename).read()
        for atom in system.ions:
            vtkField.add_atom(atom.label, atom.pos, self.ren)
        self.openedFiles[filename]["contour"] = vtkField.add_field(system.field, self.ren,k=i)
        self.vtkWidget.GetRenderWindow().Render()

    def initMainArea(self):
        pass
        self.vtkWidget = QVTKRenderWindowInteractor()
        self.setCentralWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(1, 1, 1)
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        self.iren.Start()


    def addFile(self, filename):
        pass


    def closeFiles(self):
        print("Closing Files")
        self.ren.RemoveAllViewProps()
        self.vtkWidget.GetRenderWindow().Render()
        self.openedFiles = {}
        pass
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ui = PbcPyQt()
    sys.exit(app.exec_())
