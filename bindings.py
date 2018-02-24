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
import inspect
# Qt imports
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, \
                            QPushButton, QLabel, QMessageBox
# SQLAlchemy imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, \
                       inspect as sqla_inspect
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

    def __init__(self, field, ui):
        self._field = field
        self._ui = ui
        self._name = self.__class__.__name__.lower().replace("mapper", "")
        self._autoupdate = True

    @property
    def autoupdate(self):
        return self._autoupdate

    def enable_autoupdate(self):
        self._autoupdate = True

    def disable_autoupdate(self):
        self._autoupdate = False

    @property
    def name(self):
        return self._name

    @property
    @abstractmethod
    def value(self):
        pass

    @value.setter
    @abstractmethod
    def value(self, new_value):
        pass

    @property
    @abstractmethod
    def signal(self):
        pass

    @abstractmethod
    def disable(self):
        pass

    @abstractmethod
    def enable(self):
        pass

    @property
    def reset(self):
        return None

    def isValid(self):
        try:
            # we must check what we see in order to prevent
            # can't reset issues
            # (we write 1, delete it, fails but 1 still there)
            setattr(self._ui.model, self.name, self.value)
        except Exception as e:
            print(" attribute %s value \"%s\" is invalid" % (
                self.name, self.value))
            import traceback
            traceback.print_exc()
            return False
        else:
            print(" attribute %s is valid" % self.name)
            return True

    def valid(self):
        self._field.setStyleSheet('QLineEdit { background-color: %s }' %
                                  STATES_COLORS[2])

    def schrodinger(self):
        self._field.setStyleSheet('QLineEdit { background-color: %s }' %
                                  STATES_COLORS[1])

    def invalid(self):
        self._field.setStyleSheet('QLineEdit { background-color: %s }' %
                                  STATES_COLORS[0])

    def _on_update_fail(self, exc, value):
        self.invalid()
        print(" not valid: %s" % str(exc))

    def _on_update_success(self, value):
        self.valid()
        print(" valid")

    def _on_update(self, value):
        print(" completed edit: model.%s = %s" % (self.name,
              getattr(self._ui.model, self.name)))
        self._ui.update_status()

    def _on_update_reset_fail(self, exc, value):
        print(" can't reset attribute: %s" % str(exc))

    def _on_update_reset_success(self, value):
        print(" reset attribute to %s", self.reset)

    def _on_update_reset(self, value):
        print(" completed reset")

    def updater(self):
        if not self._autoupdate:
            print("Autoupdate disabled")
            return
        print("Updating field \"%s\"" % self.name)
        model, name, value = self._ui.model, self.name, self.value
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

    @value.setter
    def value(self, new_value):
        self._field.setText(str(new_value))

    @property
    def signal(self):
        return self._field.textChanged

    def disable(self):
        self._field.setReadOnly(True)

    def enable(self):
        self._field.setReadOnly(False)


class NumberMapper(QtDataMapper):
    @property
    def value(self):
        return self._field.text()

    @value.setter
    def value(self, new_value):
        self._field.setText(str(new_value))

    @property
    def signal(self):
        return self._field.textChanged

    def disable(self):
        self._field.setReadOnly(True)

    def enable(self):
        self._field.setReadOnly(False)


# # Create widget
class ExampleDataUI():
    def setupUi(self, parent, cls_obj):
        # Create model
        if inspect.isclass(cls_obj):
            self.model = cls_obj()
        elif isinstance(cls_obj, Base):
            self.model = cls_obj
        # Window title
        self.parent = parent
        parent.setWindowTitle("SQLAlchemy + Qt test")
        # Window elements
        self.verticalLayout = QVBoxLayout(parent)
        self.titleLabel = QLabel(cls_obj.__name__, parent)
        self.emailLineEdit = QLineEdit(parent)
        self.numberLineEdit = QLineEdit(parent)
        self.statusLabel = QLabel(parent)
        self.saveButton = QPushButton("Save", parent)
        self.validateButton = QPushButton("Validate", parent)
        self.refreshButton = QPushButton("Refresh", parent)
        # Add elements to layout
        self.verticalLayout.addWidget(self.titleLabel)
        self.verticalLayout.addWidget(self.emailLineEdit)
        self.verticalLayout.addWidget(self.numberLineEdit)
        self.verticalLayout.addWidget(self.saveButton)
        self.verticalLayout.addWidget(self.refreshButton)
        self.verticalLayout.addWidget(self.validateButton)
        self.verticalLayout.addWidget(self.statusLabel)
        # Define mappings
        self.mappers = [EmailMapper(self.emailLineEdit, self),
                        NumberMapper(self.numberLineEdit, self)]
        # Create updaters and events
        for mapper in self.mappers:
            mapper.signal.connect(functools.partial(mapper.updater))
            mapper.updater()
        # Save
        self.saveButton.clicked.connect(self.save)
        self.refreshButton.clicked.connect(self.refresh)
        self.validateButton.clicked.connect(self.validate)
        self.emailLineEdit.returnPressed.connect(self.save)
        self.numberLineEdit.returnPressed.connect(self.save)
        # Set status
        self.update_status()

    def validate(self):
        for mapper in self.mappers:
            mapper.disable()
            mapper.valid()
            mapper.value = mapper.value
            mapper.enable()

    def refresh(self):
        SESSION.refresh(self.model)
        self.update_from_model()
        self.validate()
        self.update_status()

    def update_from_model(self):
        for mapper in self.mappers:
            mapper.disable()
            mapper.disable_autoupdate()
            mapper.value = getattr(self.model, mapper.name)
            mapper.schrodinger()
            mapper.enable_autoupdate()
            mapper.enable()

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
        # not necessary to check not already in session, idempotent
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
                QMessageBox.critical(self.parent,
                                     "Couldn't rollback either", str(e))
        else:
            QMessageBox.information(self.parent,
                                    "Update performed", "Congrats")
        self.update_status()

    def update_status(self):
        stat = sqla_inspect(self.model)
        stat_msg = "<b>ERROR</b>"
        if stat.transient:
            stat_msg = "Transient (not tracked)"
            self.refreshButton.hide()
            self.validateButton.show()
        elif stat.pending:
            stat_msg = "Pending (tracked but pending to add to database)"
            self.refreshButton.hide()
            self.validateButton.show()
        elif stat.persistent:
            stat_msg = "Persistent (tracked and present in database)\n"
            self.refreshButton.show()
            self.validateButton.show()
            if stat.modified:
                stat_msg += "Pending to apply changes"
            else:
                stat_msg += "No changes pending"
        elif stat.deleted:
            stat_msg = "Deleted (tracked and will be deleted)"
            self.refreshButton.show()
            self.validateButton.show()
        elif stat.detached:
            stat_msg = "Detached (untracked because deletion)"
            self.refreshButton.hide()
            self.validateButton.hide()
        self.statusLabel.setText(stat_msg)


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
