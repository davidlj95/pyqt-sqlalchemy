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
MODES = ["add", "edit-transient", "edit-pending", "edit-persistent",
         "edit-persistent-wrong"]
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
            raise ValueError("email is mandatory")
        assert '@' in address
        return address

    @validates('number')
    def validate_number(self, key, num):
        if num is None:
            return None
        return int(num)


# Qt interface
# # Mappers
class PQSFieldBinder(object):
    """PyQt-SQLAclhemy (PQS) field binder

    Binds a PyQt field object in a GUI (like a QLineEdit) to a SQLAlchemy
    field in a model.

    This allows to automatically update the SQLAlchemy field in the model when
    the PyQt field object gets update. The SQLAlchemy field can have validators
    so the GUI responds to them graphically.

    This is just a base class to define a binder. Manual bindings have to be
    set for each field in each UI created, overriding the required methods to
    provide the autoupdate feature.

    Attributes:
        __metaclass__ (class): defines this as an abstract class
        _gui_field (QWidget): PyQt object to get and set values from / to
        _ui (PQSDataUi): UI that controls the editing features and holds the
                         SQLAlchemy model
        _name (str): Name of the field we are binding in the SQLAlchemy model
        _autoupdate (bool): Controls if the SQLAlchemy will be updated
                            automatically upon detecting a change in the PyQt
                            field
    """
    CLASS_SUFFIX = "Binder"
    """
        str: suffix all derived class will have in their names so the name of
             the binded field can be guessed in `__init__` method
    """
    COLOR_INVALID = "#f6989d"
    """
        str: background color to set to a PyQt field's if the displayed value
             is invalid
    """
    COLOR_NOTVALIDATED = "#fff79a"
    """
        str: background color to set to a PyQt field's if the displayed value
             has not been checked against validity yet
    """
    COLOR_VALID = "#c4df9b"
    """
        str: background color to set to a PyQt field's if the displayed value
             is valid
    """
    VALIDITY_MARK_SYTLESHEET = "{0} {{ background-color: {1} }}"
    """
        str: stylesheet to set to a PyQt field to show graphically its validity
             default changes background color
             must format with:
                1) the PyQt field class name:
                    `self._gui_field.__class__.__name__`
                2) the color the background will be set to
    """
    __metaclass__ = ABCMeta

    def __init__(self, gui_field, ui, name=None, autoupdate=True,
                 connect_autoupdate=True):
        """Initializes a PQSFieldBinder

        Notes:
            If name is not provided, will be guessed from the class name,
            previously removing the suffix `CLASS_SUFFIX` and lowercasing it

        Args:
            gui_field (QWidget): PyQt object the SQLAlchemy model field will be
                                 binded to
            ui (class): UI that holds the SQAlchemy model and editing features
            name (str): name of the field of the SQLAlchemy model we are
                        binding
            autoupdate (bool): whether to enable autoupdate (after connecting)
            autoupdate_connect (bool): whether to connect the signal and slot
                                       to enable autoconnect
        """
        self._gui_field = gui_field
        self._ui = ui
        # Autoguess name based on CLASS_SUFFIX
        self._name = \
            self.__class__.__name__.replace(self.CLASS_SUFFIX, "").lower() \
            if name is None else name
        self._autoupdate = autoupdate
        # Autoupdate connect if needed
        if connect_autoupdate:
            self.connect_autoupdate()

    # Control the binder features
    @property
    def autoupdate(self):
        """Returns if the `autoupdate` feature is enabled"""
        return self._autoupdate

    def enable_autoupdate(self):
        """Enables the `autoupdate` feature"""
        self._autoupdate = True

    def disable_autoupdate(self):
        """Disables the `autoupdate` feature"""
        self._autoupdate = False

    def connect_autoupdate(self):
        """Connects the `gui_value_modified` signal to its trigger"""
        self.signal_autoupdate.connect(self._on_autoupdate)

    def disconnect_autoupdate(self):
        """Disconnects the `gui_value_modified` signal from its trigger"""
        self.signal_autoupdate.disconnect(self._on_autoupdate)

    # Retrieve binder properties
    @property
    def name(self):
        """Returns the name of the binded field in the SQLAlchemy model"""
        return self._name

    @property
    @abstractmethod
    def signal_autoupdate(self):
        """Returns the PyQt signal to detect a change if GUI value was modified

        Will be used to connect autoupdate signal with its event handler (slot)

        It must be overwritten so the signal is defined"""
        pass

    @property
    def model(self):
        """Returns the SQLAlchemy model object"""
        return self._ui.model

    @property
    def reset_value(self):
        """Returns the reset value in a SQLAlchemy model field

        The reset value stands for the value a field has before being
        initialized. Therefore, when we want to remove a field's value, we'll
        set it to this value.

        In SQLAlchemy, this value is `None`. You can customize it if your model
        requires specials needs but this is not recommended as your model has
        to deal with `None` value as it's the SQLAlchemy default for non-set
        values in a field
        """
        return None

    # GUI properties: set and retrieve from GUI
    @property
    @abstractmethod
    def gui_value(self):
        """Returns the value of the PyQt field object

        Must return something that can be set to the model field, providing
        the needed conversions from Qt types to Python built-in types.

        It will use one of the PyQt field's methods to retrieve a value, like
        `text()` on a `QLineEdit` object.
        """
        pass

    @gui_value.setter
    @abstractmethod
    def gui_value(self, new_value):
        """Sets the value of a PyQt field object

        Will be passed some value that may be in the SQLAlchemy model field
        and it must be able to set it in the PyQt field.

        It will use one of the PyQt field's methods to set a value, like
        `setText()` on a `QLineEdit` object.

        Notes:
            The model value can be `None` if the model's field value has not
            been set yet. The setter must set this properly and don't display
            "None" in a `QLineEdit`, but "" instead. Take care of this when
            writing fast conversions like `str(new_value)`
        """
        pass

    def update_from_gui(self):
        """Gets the GUI field value and sets it to the model

        Uses `isValid` method. Tries to reset the value to the initial value
        if can't be validated to avoid saving to the database invalid values.
        """
        value = self.gui_value
        if not self.update(value):
            self.reset()

    def update_to_gui(self):
        """Sets the GUI field value from the model's value

        Marks also the field as not validated until the value is set
        """
        value = self.model_value
        self.gui_value = value
        self.mark_as_notvalidated(value)

    # Model properties: set and retrieve from model
    @property
    def model_value(self):
        """Returns the value of the SQLAlchemy model's binded field"""
        return getattr(self.model, self.name)

    @model_value.setter
    def model_value(self, value):
        """Sets the value of the SQLAlchemy model's binded field

        Alias of `update`, without returning anything
        """
        self.update(value)

    def update(self, value=None):
        """Updates the binded model's field (and therefore also validates it)

        Like `model_value(value)`, but controls exceptions, triggers events and
        by default retrieves the value using the `gui_value` property

        If no exception is triggered, the value therefore has been set to the
        model and therefore has been validated if a validator existed. Then,
        returns True. If an exception is triggered, returns False.

        Notes:
            Event-driven methods `self._on_invalid` and `self._on_valid` will
            be triggered depending whether the operation succeeds or not.

            Event-driven methods `self.on_valid` and `self.on_invalid` will be
            triggered afterwards the previous ones (one or other depending the
            validation result)

        Args:
            value (object): value to set to the model

        Returns:
            bool: True if PyQt's field value can be set to the SQLAlchemy model
            field (therefore validates), False if not.
        """
        # Get value
        value = self.gui_value if value is None else value
        # Try to set it
        try:
            setattr(self.model, self.name, value)
        except Exception as exc:
            self._on_invalid(value, exc)
            return False
        else:
            self._on_valid(value)
            return True
        finally:
            self._ui.update_status()

    def reset(self):
        """Resets the SQLAlchemy model field's value

        Sets the field's value of the model to `reset_value` property value.
        It may fail if the field can't be blank.

        Notes:
            Event-driven methods `self._on_reset_success` and
            `self._on_reset_fail` will be triggered depending whether the
            operation succeeds or not. `self._on_reset` will always be called
            at the end.

            Event-driven methods `self.on_reset_success` and
            `self.on_reset_fail` will be triggered depending whether the
            operation succeeds or not. `self.on_reset` will always be called
            at the end

        Returns:
            bool: True if succeeds, False if not
        """
        try:
            self.model_value = self.reset_value
        except Exception as exc:
            self._on_reset_fail(exc)
        else:
            self._on_reset_success()
        finally:
            self._on_reset()

    # Control GUI: set GUI properties
    @abstractmethod
    def disable_edit(self):
        """Disables the PyQt field so the user can't write in it

        For instance, in a `QLineEdit`, the method would call
        `setReadOnly(False)` on it
        """
        pass

    def disable(self):
        """Disables the PyQt field so the user can't write in it

        Autoupdate will be also disabled
        """
        self.disable_edit()
        self.disable_autoupdate()

    @abstractmethod
    def enable_edit(self):
        """Enables the PyQt field so the user can write in it

        For instance, in a `QLineEdit`, the method would call
        `setReadOnly(True)` on it
        """
        pass

    def enable(self):
        """Enables the PyQt field so the user can write in it

        Autoupdate will be also enabled
        """
        self.enable_edit()
        self.enable_autoupdate()

    def mark_as_valid(self, value):
        """Marks the PyQt field as valid to the user, modifying it

        Args:
            value (object): value set and valid
        """
        self._gui_field.setStyleSheet(self.VALIDITY_MARK_SYTLESHEET.format(
            self._gui_field.__class__.__name__,
            self.COLOR_VALID)
        )

    def mark_as_notvalidated(self, value):
        """Marks the PyQt field as intermediate to the user, modifying it

        Intermediate status is for a field that has not been validated

        Args:
            value (object): value set and not checked against validity
        """
        self._gui_field.setStyleSheet(self.VALIDITY_MARK_SYTLESHEET.format(
            self._gui_field.__class__.__name__,
            self.COLOR_NOTVALIDATED)
        )

    def mark_as_invalid(self, value, exc):
        """Marks the PyQt field as invalid to the user, modifying it

        Args:
            value (object); value checked as invalid
            exc (Exception): exception triggered so it is marked as invalid
        """
        print("invalid")
        self._gui_field.setStyleSheet(self.VALIDITY_MARK_SYTLESHEET.format(
            self._gui_field.__class__.__name__,
            self.COLOR_INVALID)
        )

    # Event handlers
    # # Reset
    # # # Fixed
    def _on_reset_success(self):
        """Event triggered when model's value has been reseted

        Default is to call the user-defined event
        """
        self.on_reset_success()

    def _on_reset_fail(self, exc):
        """Event triggered when model's value has to be reseted but fails

        Default is to call the user-defined event

        Args:
            exc (Exception): exception triggered so it couldn't be reset
        """
        self.on_reset_fail()

    def _on_reset(self):
        """Event triggered when model's value has tried to be reseted

        Default is to call the user-defined event
        """
        self.on_reset()

    # # # User-defined
    def on_reset_success(self):
        """User event triggered when model's value has been reseted

        It triggers just after `_on_reset_success` has been called
        """
        pass

    def on_reset_fail(self, exc):
        """User event triggered when model's value has to be reseted but fails

        It triggers just after `_on_reset_fail` has been called

        Args:
            exc (Exception): exception triggered so it couldn't be reset
        """
        pass

    def on_reset(self):
        """User event triggered when model's value has tried to be reseted

        It triggers just after `_on_reset` has been called
        """
        pass

    # # Validation
    # # # Fixed
    def _on_valid(self, value):
        """Event triggered when the field value has been validated

        Default is to mark the PyQt field as valid and call the user-defined
        event

        Args:
            value (object): value set and valid
        """
        self.mark_as_valid(value)
        self.on_valid(value)

    def _on_invalid(self, value, exc):
        """Event triggered when the field value has been invalidated

        Default is to mark the PyQt field as invalid and call the user-defined
        event

        Args:
            value (object); value checked as invalid
            exc (Exception): exception triggered so it is marked as invalid
        """
        import traceback
        traceback.print_exc()
        self.mark_as_invalid(value, exc)
        self.on_invalid(value, exc)

    # # # User-defined
    def on_valid(self, value):
        """User event triggered when the field value has been validated

        It triggers just after `_on_valid` has been called

        Args:
            value (object): value set and valid
        """
        pass

    def on_invalid(self, value, exc):
        """User event triggered when the field value has been invalidated

        It triggers just after `_on_invalid` has been called

        Args:
            value (object); value checked as invalid
            exc (Exception): exception triggered so it is marked as invalid
        """
        pass

    # # Autoupdate-related
    # # # Fixed events
    def _on_autoupdate(self):
        """Triggered when we must autoupdate

        Calls `update_from_gui` if autoupdate is enabled

        Slot to connect to defined `signal_autoupdate`
        """
        if self.autoupdate:
            self.update_from_gui()


class EmailBinder(PQSFieldBinder):
    @property
    def gui_value(self):
        get_value = self._gui_field.text()
        return get_value if len(get_value) else None

    @gui_value.setter
    def gui_value(self, new_value):
        set_value = new_value
        if new_value is None:
            set_value = ""
        elif not isinstance(new_value, str):
            set_value = str(set_value)
        self._gui_field.setText(set_value)

    @property
    def signal_autoupdate(self):
        return self._gui_field.textChanged

    def disable_edit(self):
        self._gui_field.setReadOnly(True)

    def enable_edit(self):
        self._gui_field.setReadOnly(False)


class NumberBinder(PQSFieldBinder):
    @property
    def gui_value(self):
        get_value = self._gui_field.text()
        return get_value if len(get_value) else None

    @gui_value.setter
    def gui_value(self, new_value):
        set_value = new_value
        if new_value is None:
            set_value = ""
        elif not isinstance(new_value, str):
            set_value = str(set_value)
        self._gui_field.setText(set_value)

    @property
    def signal_autoupdate(self):
        return self._gui_field.textChanged

    def disable_edit(self):
        self._gui_field.setReadOnly(True)

    def enable_edit(self):
        self._gui_field.setReadOnly(False)


# # Create widget
class ExampleDataUI():
    def __init__(self, cls_obj):
        # Create model
        if inspect.isclass(cls_obj):
            print("ui started with class %s" % cls_obj.__name__)
            self.model = cls_obj()
        elif isinstance(cls_obj, Base):
            print("ui started with object %s" % cls_obj)
            self.model = cls_obj

    def setupUi(self, parent):
        # Window title
        self.parent = parent
        parent.setWindowTitle("SQLAlchemy + Qt test")
        # Window elements
        self.verticalLayout = QVBoxLayout(parent)
        self.titleLabel = QLabel(self.model.__class__.__name__, parent)
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
        self.mappers = [EmailBinder(self.emailLineEdit, self),
                        NumberBinder(self.numberLineEdit, self)]
        # Fill GUI
        for mapper in self.mappers:
            mapper.disable()
            mapper.update_to_gui()
            mapper.enable()
            status = sqla_inspect(self.model)
            print(status.modified)
            if status.persistent and not status.modified:
                # Do not update if persistent and clean
                self.update_status()
            else:
                mapper.update()
        # Save
        self.saveButton.clicked.connect(self.save)
        self.refreshButton.clicked.connect(self.refresh)
        self.validateButton.clicked.connect(self.validate)
        self.emailLineEdit.returnPressed.connect(self.save)
        self.numberLineEdit.returnPressed.connect(self.save)

    def validate(self):
        for mapper in self.mappers:
            mapper.disable_edit()
            mapper.update()
            mapper.enable_edit()

    def refresh(self):
        SESSION.refresh(self.model)
        self.update_to_gui()
        self.update_status()

    def update_to_gui(self):
        for mapper in self.mappers:
            mapper.disable()
            mapper.update_to_gui()
            mapper.enable()

    def save(self):
        print("Try to save")
        for mapper in self.mappers:
            if not mapper.update():
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
    mode = MODES[0]
    # # args
    if len(sys.argv) > 1:
        if sys.argv[1] in MODES:
            mode = sys.argv[1]
        else:
            print("unknown mode")
            print("choose from %s" % str(MODES))
            sys.exit(1)
    # # SQLAlchemy
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    SESSION = Session()
    # # Qt
    app = QApplication(sys.argv)
    widget = QWidget()
    print("ui mode: %s" % mode)
    if mode == "add":
        ui = ExampleDataUI(User)
    elif mode == "edit-transient":
        ui = ExampleDataUI(User(email="transient@users.org", number=1))
    elif mode == "edit-pending":
        u = User(email="pending@users.org", number=2)
        SESSION.add(u)
        ui = ExampleDataUI(u)
    elif mode == "edit-persistent":
        u = User(email="persistent@users.org", number=3)
        SESSION.add(u)
        SESSION.commit()
        ui = ExampleDataUI(u)
    elif mode == "edit-persistent-wrong":
        SESSION.execute("INSERT INTO users (email, number) VALUES (" +
                        "\"persistent-wrongusers.org\", 4)")
        SESSION.commit()
        u = SESSION.query(User).first()
        ui = ExampleDataUI(u)
    ui.setupUi(widget)
    widget.show()
    # run and show
    sys.exit(app.exec_())
