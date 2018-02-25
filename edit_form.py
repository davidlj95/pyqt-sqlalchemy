# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_form.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PQSEditUI(object):
    def setupUi(self, PQSEditUI):
        PQSEditUI.setObjectName("PQSEditUI")
        PQSEditUI.resize(400, 127)
        self.verticalLayout = QtWidgets.QVBoxLayout(PQSEditUI)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QtWidgets.QLabel(PQSEditUI)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)
        self.line = QtWidgets.QFrame(PQSEditUI)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.formWidget = QtWidgets.QWidget(PQSEditUI)
        self.formWidget.setObjectName("formWidget")
        self.verticalLayout.addWidget(self.formWidget)
        self.line_2 = QtWidgets.QFrame(PQSEditUI)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtWidgets.QPushButton(PQSEditUI)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.validateButton = QtWidgets.QPushButton(PQSEditUI)
        self.validateButton.setObjectName("validateButton")
        self.horizontalLayout.addWidget(self.validateButton)
        self.refreshButton = QtWidgets.QPushButton(PQSEditUI)
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout.addWidget(self.refreshButton)
        self.deleteButton = QtWidgets.QPushButton(PQSEditUI)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout.addWidget(self.deleteButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.statusLabel = QtWidgets.QLabel(PQSEditUI)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.statusLabel.setFont(font)
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.statusLabel.setObjectName("statusLabel")
        self.verticalLayout.addWidget(self.statusLabel)

        self.retranslateUi(PQSEditUI)
        QtCore.QMetaObject.connectSlotsByName(PQSEditUI)

    def retranslateUi(self, PQSEditUI):
        _translate = QtCore.QCoreApplication.translate
        PQSEditUI.setWindowTitle(_translate("PQSEditUI", "PyQt - SQLAlchemy binder"))
        self.titleLabel.setText(_translate("PQSEditUI", "Edit Title"))
        self.saveButton.setText(_translate("PQSEditUI", "Save"))
        self.validateButton.setText(_translate("PQSEditUI", "Validate"))
        self.refreshButton.setText(_translate("PQSEditUI", "Refresh"))
        self.deleteButton.setText(_translate("PQSEditUI", "Delete"))
        self.statusLabel.setText(_translate("PQSEditUI", "Status"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PQSEditUI = QtWidgets.QWidget()
    ui = Ui_PQSEditUI()
    ui.setupUi(PQSEditUI)
    PQSEditUI.show()
    sys.exit(app.exec_())

