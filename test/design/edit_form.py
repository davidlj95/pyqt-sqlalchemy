# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test/ui/edit_form.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditForm(object):
    def setupUi(self, EditForm):
        EditForm.setObjectName("EditForm")
        EditForm.resize(400, 127)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QtWidgets.QLabel(EditForm)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)
        self.line = QtWidgets.QFrame(EditForm)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.formWidget = QtWidgets.QWidget(EditForm)
        self.formWidget.setObjectName("formWidget")
        self.verticalLayout.addWidget(self.formWidget)
        self.line_2 = QtWidgets.QFrame(EditForm)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtWidgets.QPushButton(EditForm)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.validateButton = QtWidgets.QPushButton(EditForm)
        self.validateButton.setObjectName("validateButton")
        self.horizontalLayout.addWidget(self.validateButton)
        self.refreshButton = QtWidgets.QPushButton(EditForm)
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout.addWidget(self.refreshButton)
        self.deleteButton = QtWidgets.QPushButton(EditForm)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout.addWidget(self.deleteButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.statusLabel = QtWidgets.QLabel(EditForm)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.statusLabel.setFont(font)
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.statusLabel.setObjectName("statusLabel")
        self.verticalLayout.addWidget(self.statusLabel)

        self.retranslateUi(EditForm)
        QtCore.QMetaObject.connectSlotsByName(EditForm)

    def retranslateUi(self, EditForm):
        _translate = QtCore.QCoreApplication.translate
        EditForm.setWindowTitle(_translate("EditForm", "PyQt - SQLAlchemy binder"))
        self.titleLabel.setText(_translate("EditForm", "Edit Title"))
        self.saveButton.setText(_translate("EditForm", "Save"))
        self.validateButton.setText(_translate("EditForm", "Validate"))
        self.refreshButton.setText(_translate("EditForm", "Refresh"))
        self.deleteButton.setText(_translate("EditForm", "Delete"))
        self.statusLabel.setText(_translate("EditForm", "Status"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EditForm = QtWidgets.QWidget()
    ui = Ui_EditForm()
    ui.setupUi(EditForm)
    EditForm.show()
    sys.exit(app.exec_())

