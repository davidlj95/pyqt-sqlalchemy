# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_form.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditUI(object):
    def setupUi(self, EditUI):
        EditUI.setObjectName("EditUI")
        EditUI.resize(400, 127)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditUI)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QtWidgets.QLabel(EditUI)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)
        self.line = QtWidgets.QFrame(EditUI)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.formWidget = QtWidgets.QWidget(EditUI)
        self.formWidget.setObjectName("formWidget")
        self.verticalLayout.addWidget(self.formWidget)
        self.line_2 = QtWidgets.QFrame(EditUI)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtWidgets.QPushButton(EditUI)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.validateButton = QtWidgets.QPushButton(EditUI)
        self.validateButton.setObjectName("validateButton")
        self.horizontalLayout.addWidget(self.validateButton)
        self.refreshButton = QtWidgets.QPushButton(EditUI)
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout.addWidget(self.refreshButton)
        self.deleteButton = QtWidgets.QPushButton(EditUI)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout.addWidget(self.deleteButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.statusLabel = QtWidgets.QLabel(EditUI)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.statusLabel.setFont(font)
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.statusLabel.setObjectName("statusLabel")
        self.verticalLayout.addWidget(self.statusLabel)

        self.retranslateUi(EditUI)
        QtCore.QMetaObject.connectSlotsByName(EditUI)

    def retranslateUi(self, EditUI):
        _translate = QtCore.QCoreApplication.translate
        EditUI.setWindowTitle(_translate("EditUI", "PyQt - SQLAlchemy binder"))
        self.titleLabel.setText(_translate("EditUI", "Edit Title"))
        self.saveButton.setText(_translate("EditUI", "Save"))
        self.validateButton.setText(_translate("EditUI", "Validate"))
        self.refreshButton.setText(_translate("EditUI", "Refresh"))
        self.deleteButton.setText(_translate("EditUI", "Delete"))
        self.statusLabel.setText(_translate("EditUI", "Status"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EditUI = QtWidgets.QWidget()
    ui = Ui_EditUI()
    ui.setupUi(EditUI)
    EditUI.show()
    sys.exit(app.exec_())

