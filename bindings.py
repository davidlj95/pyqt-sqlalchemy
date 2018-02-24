# sources
# http://doc.qt.io/qt-5/qlineedit.html#validator
# http://doc.qt.io/qt-5/qvalidator.html
# http://doc.qt.io/qt-5/qdoublevalidator.html
# http://doc.qt.io/qt-5/qregexp.html
# http://doc.qt.io/qt-5/qintvalidator.html
# https://snorfalorpagus.net/blog/2014/08/09/validating-user-input-in-pyqt4-using-qvalidator/
# http://docs.sqlalchemy.org/en/latest/orm/mapped_attributes.html
# notes
# Generic imports
import sys
import traceback
# Qt imports
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, \
                            QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QValidator, QIntValidator, QRegExpValidator
# SQLAlchemy imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import validates, sessionmaker

# globals
STATES_COLORS = ["#f6989d", "#fff79a", "#c4df9b"]

# SQLAlchemy model
# # Launch environment
Base = declarative_base()
engine = create_engine("sqlite:///:memory:", echo=True)
# # Define model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    number = Column(Integer)

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address

# Qt interface
# # Create widget
class ExampleDataUI():
    def setupUi(self, parent, cls):
        # Window title
        self.parent = parent
        parent.setWindowTitle("SQLAlchemy + Qt test")
        # Window elements
        self.verticalLayout = QVBoxLayout(parent)
        self.titleLabel = QLabel(cls.__name__, parent)
        self.emailLineEdit = QLineEdit(parent)
        self.numberLineEdit = QLineEdit(parent)
        self.saveButton = QPushButton("Save", parent)
        # Add elements to layout
        self.verticalLayout.addWidget(self.titleLabel)
        self.verticalLayout.addWidget(self.emailLineEdit)
        self.verticalLayout.addWidget(self.numberLineEdit)
        self.verticalLayout.addWidget(self.saveButton)
        # Define mappings
        self.model = User()
        self.fieldModelMap = { self.emailLineEdit : "email" }
        self.fieldDataMap = { self.emailLineEdit : self.emailLineEdit.text }
        self.fieldSignalMap = { self.emailLineEdit: self.emailLineEdit.textChanged }
        # Create updaters and events
        for field, get_data in self.fieldDataMap.items():
                self.fieldSignalMap[field].connect(lambda: self.updater(field))
                self.updater(field)

    def updater(self, field):
        print("updating")
        value = self.fieldDataMap[field]()
        attribute = self.fieldModelMap[field]
        color = STATES_COLORS[2]
        try:
            setattr(self.model, attribute, value)
            print(" valid")
        except Exception as e:
            color = STATES_COLORS[0]
            print(" not valid")
        try:
            setattr(self.model, attribute, None)
        except Exception as e:
            print(" can't reset variable")
        print(" result: model.%s = %s" % (attribute, getattr(self.model, attribute)))
        field.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def update_state(self, sender, val):
        # Check state and update
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        color = STATES_COLORS[state]
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

# run
if __name__ == "__main__":
    # prepare scenario
    # # SQLAlchemy
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # # Qt
    app = QApplication(sys.argv)
    widget = QWidget()
    ui = ExampleDataUI()
    ui.setupUi(widget, User)
    widget.show()
    # run and show
    sys.exit(app.exec_())
