#!/usr/bin/env python

import sys
import os
from collections import OrderedDict

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QFileDialog, QLabel,
                            QApplication, QMainWindow, QSlider)

import pbcpy_vtk
from pbcpy.formats.qepp import PP


class PbcPyQt(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.openedFiles = {}
        self.isoValue = 10.**-2
        self.status = "Ready"
        self.initUI()
        
        
    def initUI(self):

        self.setAcceptDrops(True)

        self.initMenuBar()
        self.initStatusBar()
        self.initVtkArea()

        self.setGeometry(500, 500, 900, 600)
        self.setWindowTitle('PbcPy')    
        self.show()

    def initMenuBar(self):
        menubar = self.menuBar()
        menubar.hide()
        toolbar = self.addToolBar("Menu")

        fileMenu = menubar.addMenu('&File')

        fileOpenAct = QAction(QIcon.fromTheme('document-open'), "&Open", self)
        fileOpenAct.triggered.connect(self.fileDialog)
        fileOpenAct.setShortcut('Ctrl+O')

        fileFolderAct = QAction(QIcon.fromTheme('folder-open'), "Open &Folder", self)
        fileFolderAct.triggered.connect(self.folderDialog)
        fileFolderAct.setShortcut('Ctrl+D')

        fileCloseAct = QAction(QIcon.fromTheme('window-close'), "&Close", self)
        fileCloseAct.triggered.connect(self.closeFiles)
        fileCloseAct.setShortcut('Ctrl+W')

        fileQuitAct = QAction(QIcon.fromTheme('application-exit'), "&Quit", self)
        fileQuitAct.setShortcut('Ctrl+Q')
        fileQuitAct.triggered.connect(QApplication.instance().quit)

        fileMenu.addActions([fileOpenAct, fileFolderAct])
        fileMenu.addSeparator()
        fileMenu.addActions([fileCloseAct,fileQuitAct])

        toolbar.addActions([fileOpenAct, fileFolderAct])
        toolbar.addSeparator()
        toolbar.addActions([fileCloseAct,fileQuitAct])


    def initStatusBar(self):
        self.statusbar = self.statusBar()
        #self.statusLabel = QLabel(self.status, self)
        self.isoLabel0 = QLabel("Iso Value: ".format(self.isoValue), self)
        self.isoLabel1 = QLabel("{}".format(self.isoValue), self)

        self.isoSlider = QSlider(Qt.Horizontal, self)
        self.isoSlider.setMaximumWidth(150)
        self.isoSlider.setRange(-5, -1)
        self.isoSlider.setValue(-2)
        self.isoSlider.valueChanged.connect(self.onIsoChange, self.isoSlider.value())

        self.statusbar.addWidget(self.isoLabel0)
        self.statusbar.addWidget(self.isoSlider)
        self.statusbar.addWidget(self.isoLabel1)
        #self.statusbar.addWidget(self.statusLabel)


    def printMsg(self):
        print("I have been clicked")

    def onIsoChange(self, n):
        self.isoValue = 10.**n
        self.isoLabel1.setText("{}".format(self.isoValue))
        for key, item in self.openedFiles.items():
            item["contour"].SetValue(0,self.isoValue)
        self.vtkWidget.GetRenderWindow().Render()


    def fileDialog(self):
        fname = QFileDialog.getOpenFileName(self, "", "", "Quantum Espresso (*.pp)")
        import time
        if fname[0]:
            self.processFile(fname[0])

    def folderDialog(self):
        dialog = QFileDialog()
        dirname = dialog.getExistingDirectory(None, "Select Folder")
        if dirname:
            self.processFolder(dirname)


    def processFolder(self, dirname):
        for f in os.listdir(dirname):
            self.processFile(os.path.join(dirname, f))


    def processFile(self, filename):
        if not filename.endswith(".pp"):
            return
        if filename in self.openedFiles:
            return

        i = len(self.openedFiles)
        self.openedFiles[filename] = {}

        #self.statusLabel.setText("Loading")

        system = PP(filename).read()

        if i == 0:
            pbcpy_vtk.add_cell(system.cell, self.ren)

        for atom in system.ions:
            pbcpy_vtk.add_atom(atom.label, atom.pos, self.ren)

        self.openedFiles[filename]["contour"] = pbcpy_vtk.add_field(system.field, self.ren, iso=self.isoValue , k=i)
        self.vtkWidget.GetRenderWindow().Render()

        #self.statusLabel.setText("Ready")


    def initVtkArea(self):
        self.vtkWidget = QVTKRenderWindowInteractor()
        self.setCentralWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.9, 0.9, 0.9)
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        self.iren.Start()


    def closeFiles(self):
        print("Closing Files")
        self.ren.RemoveAllViewProps()
        self.vtkWidget.GetRenderWindow().Render()
        self.openedFiles = {}


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for f in event.mimeData().urls():
            path = f.toLocalFile()
            if os.path.isdir(path):
                self.processFolder(path)
            elif os.path.isfile(path):
                self.processFile(path)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Alt:
            if self.menuBar().isVisible():
                self.menuBar().hide()
            else:
                self.menuBar().show()
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ui = PbcPyQt()
    sys.exit(app.exec_())