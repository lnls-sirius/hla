# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'example.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QAction, QMenu
from PyQt5.QtCore import Qt

app = QApplication([])
wid = QWidget()
pb = QPushButton(wid)
pb.setContextMenuPolicy(Qt.CustomContextMenu)
menu = QMenu('test')
menu.addAction('exit')
menu2 = menu.addMenu('testing')
action = menu2.addAction('test')
#pb.customContextMenuRequested.connect(menu.exec_)
pb.setMenu(menu)
pb.clicked.connect(pb.showMenu)
wid.show()
sys.exit(app.exec_())
