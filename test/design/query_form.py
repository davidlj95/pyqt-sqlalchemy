# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test/ui/query_form.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_QueryForm(object):
    def setupUi(self, QueryForm):
        QueryForm.setObjectName("QueryForm")
        QueryForm.resize(544, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(QueryForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QtWidgets.QLabel(QueryForm)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.queryColumnComboBox = QtWidgets.QComboBox(QueryForm)
        self.queryColumnComboBox.setObjectName("queryColumnComboBox")
        self.horizontalLayout_3.addWidget(self.queryColumnComboBox)
        self.queryOperatorComboBox = QtWidgets.QComboBox(QueryForm)
        self.queryOperatorComboBox.setObjectName("queryOperatorComboBox")
        self.horizontalLayout_3.addWidget(self.queryOperatorComboBox)
        self.queryLineEdit = QtWidgets.QLineEdit(QueryForm)
        self.queryLineEdit.setObjectName("queryLineEdit")
        self.horizontalLayout_3.addWidget(self.queryLineEdit)
        self.queryButton = QtWidgets.QPushButton(QueryForm)
        self.queryButton.setObjectName("queryButton")
        self.horizontalLayout_3.addWidget(self.queryButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.resultsTableView = QtWidgets.QTableView(QueryForm)
        self.resultsTableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.resultsTableView.setObjectName("resultsTableView")
        self.verticalLayout.addWidget(self.resultsTableView)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(QueryForm)
        QtCore.QMetaObject.connectSlotsByName(QueryForm)

    def retranslateUi(self, QueryForm):
        _translate = QtCore.QCoreApplication.translate
        QueryForm.setWindowTitle(_translate("QueryForm", "Form"))
        self.titleLabel.setText(_translate("QueryForm", "Query Form"))
        self.queryButton.setText(_translate("QueryForm", "Query"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    QueryForm = QtWidgets.QWidget()
    ui = Ui_QueryForm()
    ui.setupUi(QueryForm)
    QueryForm.show()
    sys.exit(app.exec_())

