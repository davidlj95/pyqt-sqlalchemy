# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'user_form.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_UserForm(object):
    def setupUi(self, UserForm):
        UserForm.setObjectName("UserForm")
        UserForm.resize(305, 186)
        self.verticalLayout = QtWidgets.QVBoxLayout(UserForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.emailLabel = QtWidgets.QLabel(UserForm)
        self.emailLabel.setObjectName("emailLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.emailLabel)
        self.emailLineEdit = QtWidgets.QLineEdit(UserForm)
        self.emailLineEdit.setObjectName("emailLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.emailLineEdit)
        self.numberLabel = QtWidgets.QLabel(UserForm)
        self.numberLabel.setObjectName("numberLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.numberLabel)
        self.numberLineEdit = QtWidgets.QLineEdit(UserForm)
        self.numberLineEdit.setObjectName("numberLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.numberLineEdit)
        self.birthdateDateEdit = QtWidgets.QDateEdit(UserForm)
        self.birthdateDateEdit.setObjectName("birthdateDateEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.birthdateDateEdit)
        self.genderLabel = QtWidgets.QLabel(UserForm)
        self.genderLabel.setObjectName("genderLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.genderLabel)
        self.genderWidget = QtWidgets.QWidget(UserForm)
        self.genderWidget.setObjectName("genderWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.genderWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.femaleRadioButton = QtWidgets.QRadioButton(self.genderWidget)
        self.femaleRadioButton.setObjectName("femaleRadioButton")
        self.horizontalLayout.addWidget(self.femaleRadioButton)
        self.maleRadioButton = QtWidgets.QRadioButton(self.genderWidget)
        self.maleRadioButton.setObjectName("maleRadioButton")
        self.horizontalLayout.addWidget(self.maleRadioButton)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.genderWidget)
        self.birthdateLabel = QtWidgets.QLabel(UserForm)
        self.birthdateLabel.setObjectName("birthdateLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.birthdateLabel)
        self.idLabel = QtWidgets.QLabel(UserForm)
        self.idLabel.setObjectName("idLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.idLabel)
        self.idLineEdit = QtWidgets.QLineEdit(UserForm)
        self.idLineEdit.setReadOnly(True)
        self.idLineEdit.setObjectName("idLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.idLineEdit)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(UserForm)
        QtCore.QMetaObject.connectSlotsByName(UserForm)

    def retranslateUi(self, UserForm):
        _translate = QtCore.QCoreApplication.translate
        UserForm.setWindowTitle(_translate("UserForm", "Form"))
        self.emailLabel.setText(_translate("UserForm", "email"))
        self.numberLabel.setText(_translate("UserForm", "number"))
        self.birthdateDateEdit.setDisplayFormat(_translate("UserForm", "dd/MM/yyyy"))
        self.genderLabel.setText(_translate("UserForm", "gender"))
        self.femaleRadioButton.setText(_translate("UserForm", "female"))
        self.maleRadioButton.setText(_translate("UserForm", "male"))
        self.birthdateLabel.setText(_translate("UserForm", "birthdate"))
        self.idLabel.setText(_translate("UserForm", "id"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    UserForm = QtWidgets.QWidget()
    ui = Ui_UserForm()
    ui.setupUi(UserForm)
    UserForm.show()
    sys.exit(app.exec_())

