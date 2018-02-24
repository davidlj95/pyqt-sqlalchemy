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
from abc import ABCMeta, abstractmethod
import sys
import functools
# Qt imports
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, \
                            QPushButton, QLabel, QMessageBox
# SQLAlchemy imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import validates, sessionmaker

# globals
SESSION = None
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
        if address is None:
            return None
        if address == "":
            return None
        assert '@' in address
        return address

    @validates('number')
    def validate_number(self, key, num):
        if num is None:
            return None
        return int(num)


# Qt interface
# # Mappers
class QtDataMapper(object):
    __metaclass__ = ABCMeta

    def __init__(self, field, model):
        self._field = field
        self._model = model
        self._name = self.__class__.__name__.lower().replace("mapper", "")

    @property
    def name(self):
        return self._name

    @property
    @abstractmethod
    def value(self):
        pass

    @property
    @abstractmethod
    def signal(self):
        pass

    @property
    def reset(self):
        return None

    def isValid(self):
        try:
            # we must check what we see in order to prevent
            # unresettable issues (we write 1, delete it, fails but 1 still there)
            setattr(self._model, self.name, self.value)
        except Exception as e:
            print(" attribute %s value \"%s\" is invalid" % (self.name, self.value))
            import traceback
            traceback.print_exc()
            return False
        else:
            print(" attribute %s is valid" % self.name)
            return True

    def _on_update_fail(self, exc, value):
        self._field.setStyleSheet('QLineEdit { background-color: %s }' %
                                  STATES_COLORS[0])
        print(" not valid: %s" % str(exc))

    def _on_update_success(self, value):
        self._field.setStyleSheet('QLineEdit { background-color: %s }' %
                                  STATES_COLORS[2])
        print(" valid")

    def _on_update(self, value):
        print(" completed edit: model.%s = %s" % (self.name,
              getattr(self._model, self.name)))

    def _on_update_reset_fail(self, exc, value):
        print(" can't reset attribute: %s" % str(exc))

    def _on_update_reset_success(self, value):
        print(" reset attribute to %s", self.reset)

    def _on_update_reset(self, value):
        print(" completed reset")

    def updater(self):
        print("Updating field \"%s\"" % self.name)
        model, name, value = self._model, self.name, self.value
        failed = False
        # try to set value
        try:
            setattr(model, name, value)
        except Exception as exc:
            self._on_update_fail(exc, value)
            failed = True
        else:
            self._on_update_success(value)
        # try to reset if failed
        if failed:
            try:
                setattr(model, name, self.reset)
            except Exception as exc:
                self._on_update_reset_fail(exc, value)
            else:
                self._on_update_reset_success(value)
            finally:
                self._on_update_reset(value)
        # finished update
        self._on_update(value)


class EmailMapper(QtDataMapper):
    @property
    def value(self):
        return self._field.text()

    @property
    def signal(self):
        return self._field.textChanged


class NumberMapper(QtDataMapper):
    @property
    def value(self):
        return self._field.text()

    @property
    def signal(self):
        return self._field.textChanged


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
        self.mappers = [EmailMapper(self.emailLineEdit, self.model),
                        NumberMapper(self.numberLineEdit, self.model)]
        # Create updaters and events
        for mapper in self.mappers:
            mapper.signal.connect(functools.partial(mapper.updater))
            mapper.updater()
        # Save
        self.saveButton.clicked.connect(self.save)
        self.emailLineEdit.returnPressed.connect(self.save)
        self.numberLineEdit.returnPressed.connect(self.save)

    def save(self):
        print("Try to save")
        for mapper in self.mappers:
            if not mapper.isValid():
                QMessageBox.warning(self.parent, "Form invalid",
                                    "Check and try again")
                return
        self.save_to_db()

    def save_to_db(self):
        print("Saving to db")
        SESSION.add(self.model)
        rollback = False
        try:
            SESSION.commit()
        except Exception as e:
            rollback = True
            QMessageBox.critical(self.parent, "Couldn't send to db", str(e))
        if rollback:
            try:
                SESSION.rollback()
            except Exception as e:
                QMessageBox.critical(self.parent, "Couldn't rollback either", str(e))
        else:
            QMessageBox.information(self.parent, "Update performed", "Congrats")

# run
if __name__ == "__main__":
    # prepare scenario
    # # SQLAlchemy
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    SESSION = Session()
    # # Qt
    app = QApplication(sys.argv)
    widget = QWidget()
    ui = ExampleDataUI()
    ui.setupUi(widget, User)
    widget.show()
    # run and show
    sys.exit(app.exec_())
