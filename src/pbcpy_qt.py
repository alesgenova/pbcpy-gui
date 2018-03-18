#!/usr/bin/env python

import sys
import os
from collections import OrderedDict

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QAction, QFileDialog, QLabel,
                            QApplication, QMainWindow, QSlider,
                            QSplitter, QFrame, QListWidget,
                            QListView)


import pbcpy_vtk
from pbcpy.formats.qepp import PP


class PbcPyQt(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.openedFiles = OrderedDict()
        self.isoValue = 10.**-2
        self.status = "Ready"
        self.initUI()
        

    def initUI(self):

        self.setAcceptDrops(True)

        self.initMenuBar()
        self.initStatusBar()
        self.initMainArea()

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
            item.contour.SetValue(0,self.isoValue)
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
        files = os.listdir(dirname)
        files.sort()
        for f in files:
            f = os.path.join(dirname, f)
            if os.path.isfile(f):
                self.processFile(f)


    def processFile(self, filename):
        if not filename.endswith(".pp"):
            return
        if filename in self.openedFiles:
            return

        i = len(self.openedFiles)
        #self.openedFiles[filename] = {}

        #self.statusLabel.setText("Loading")

        system = PP(filename).read()

        if i == 0:
            pbcpy_vtk.add_cell(system.cell, self.ren)

        for atom in system.ions:
            pbcpy_vtk.add_atom(atom.label, atom.pos, self.ren)

        self.openedFiles[filename] = pbcpy_vtk.add_field(system.field, self.ren,
                                                         iso=self.isoValue , k=i, filename=filename)
        self.vtkWidget.GetRenderWindow().Render()

        self.addListItem(self.openedFiles[filename])

        #self.statusLabel.setText("Ready")

    def initMainArea(self):
        self.splitter = QSplitter(Qt.Horizontal)
        self.initVtkArea()
        self.initListWidget()
        #topleft = QFrame(self)
        self.splitter.addWidget(self.listWidget)
        self.splitter.addWidget(self.vtkWidget)
        self.setCentralWidget(self.splitter)

    def initVtkArea(self):
        self.vtkWidget = QVTKRenderWindowInteractor()
        #self.setCentralWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.9, 0.9, 0.9)
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        self.iren.Start()

    def initListWidget(self):
        self.listWidget = QListView(self)
        self.listWidget.setMaximumWidth(200)
        self.listWidget.setSpacing(2)
        self.listModel = QStandardItemModel(self.listWidget)
        self.listModel.itemChanged.connect(self.onItemChanged)
        self.listWidget.setModel(self.listModel)


    def addListItem(self, subsystem):
        #self.listWidget.addItem(subsystem.shortname)
        item = QStandardItem(subsystem.shortname)
        item.setCheckable(True)
        item.setCheckState(2)
        item.setEditable(0)
        self.listModel.appendRow(item)


    def onItemChanged(self, item):
        l = list(self.openedFiles.items())
        filename, frag = l[item.row()]
        if item.checkState() == 2:
            # is checked
            self.ren.AddActor(frag.actor)
        elif item.checkState() == 0:
            # is unchecked
            self.ren.RemoveActor(frag.actor)
        self.vtkWidget.GetRenderWindow().Render()


    def closeFiles(self):
        print("Closing Files")
        self.ren.RemoveAllViewProps()
        self.vtkWidget.GetRenderWindow().Render()
        n = len(self.openedFiles)
        self.listModel.removeRows(0,n)
        self.openedFiles = OrderedDict()
        


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
