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
import inspect
import datetime
# Qt imports
from PyQt5.QtWidgets import QApplication, QWidget
# SQLAlchemy imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, \
                       inspect as sqla_inspect, Date
from sqlalchemy.orm import validates, sessionmaker, Session
# UI imports
from edit_form import Ui_PQSEditUI
from user_form import Ui_UserForm

# globals
SESSION_FACTORY = None
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
    birthdate = Column(Date)

    @validates('id')
    def validate_id(self, key, id):
        if id is None:
            return None
        try:
            id = int(id)
        except Exception as e:
            raise ValueError("unable to set id", str(id), " as number:",
                             str(e))
        return id

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

    @validates('birthdate')
    def validate_birthdate(self, key, birthdate):
        if birthdate > datetime.date.today():
            raise ValueError("You can't be born in the future")
        return birthdate


# Qt interface
# # Mappers
class PQSFieldBinder(metaclass=ABCMeta):
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
        _gui_field (QWidget): PyQt object to get and set values from / to
        _ui (PQSDataUi): UI that controls the editing features and holds the
                         SQLAlchemy model
        _name (str): Name of the field we are binding in the SQLAlchemy model
        _autoupdate (bool): Controls if the SQLAlchemy will be updated
                            automatically upon detecting a change in the PyQt
                            field
        _disabled (bool): True so the user will never be able to write here
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
    COLOR_NOT_VALIDATED = "#fff79a"
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
    __slots__ = "_gui_field", "_ui", "_name", "_autoupdate", "_disabled"

    def __init__(self, gui_field, ui, name=None, disabled=None,
                 autoupdate=True, connect_autoupdate=True, connect_save=True):
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
            disabled (bool): user can never write to this field
                             if not specified, will be determined by GUI status
            autoupdate (bool): whether to enable autoupdate (after connecting)
            autoupdate_connect (bool): whether to connect the signal and slot
                                       to enable autoconnect
            connect_save (bool): whether to connect the signal and slot to
                                   save on specified signal
        """
        self._gui_field = gui_field
        self._ui = ui
        # Autoguess name based on CLASS_SUFFIX
        self._name = \
            self.__class__.__name__.replace(self.CLASS_SUFFIX, "").lower() \
            if name is None else name
        self._autoupdate = autoupdate
        self._disabled = disabled if isinstance(disabled, bool) else \
            self.is_edit_disabled()
        # Disable field
        if self._disabled:
            self.override_disable_edit()
        # Autoupdate connect if needed
        if connect_autoupdate:
            self.connect_autoupdate()
        # Commit connect if needed
        if connect_save:
            self.connect_save()

    # Control the binder autoupdate features
    @property
    def autoupdate(self):
        """Returns if the `autoupdate` feature is enabled"""
        return self._autoupdate

    def enable_autoupdate(self):
        """Enables the `autoupdate` feature"""
        if not self._disabled:
            self._autoupdate = True

    def disable_autoupdate(self):
        """Disables the `autoupdate` feature"""
        if not self._disabled:
            self._autoupdate = False

    # Signals
    @property
    @abstractmethod
    def signal_autoupdate(self):
        """Returns the PyQt signal to detect a change if GUI value was modified

        Will be used to connect autoupdate signal with its event handler (slot)

        It must be overwritten so the signal is defined"""
        pass

    @property
    def signal_save(self):
        """Returns the PyQt signal that tells we must save changes

        Will be used to connect to save if needed.

        Can return None if no signal exists
        """
        return None

    # Auto connectors
    def connect_autoupdate(self):
        """Connects the `signal_autoupdate` signal to its trigger"""
        if not self._disabled:
            self.signal_autoupdate.connect(self._on_autoupdate)

    def disconnect_autoupdate(self):
        """Disconnects the `signal_autoupdate` signal from its trigger"""
        if not self._disabled:
            self.signal_autoupdate.disconnect(self._on_autoupdate)

    def connect_save(self):
        """Connects the `signal_save` signal to its slot"""
        signal = self.signal_save
        if signal is not None and not self._disabled:
            signal.connect(self._ui.save)

    def disconnect_save(self):
        """Disconnects the `signal_save` signal from its slot"""
        signal = self.signal_save
        if signal is not None and not self._disabled:
            signal.disconnect(self._ui.save)

    # Retrieve binder properties
    @property
    def name(self):
        """Returns the name of the binded field in the SQLAlchemy model"""
        return self._name

    @property
    def model(self):
        """Returns the SQLAlchemy model object"""
        return self._ui.model

    @property
    def disabled(self):
        """Returns if the binder is disabled (user can't edit)"""
        return self._disabled

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
        if not self._disabled:
            value = self.gui_value
            if not self.update(value):
                self.reset()

    def update_to_gui(self):
        """Sets the GUI field value from the model's value"""
        self.gui_value = self.model_value

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
    def is_edit_disabled(self):
        """Returns if edit is disabled

        Must be overriden

        Returns:
            bool: True if edit in GUI is disabled
        """
        pass

    def is_edit_enabled(self):
        """Returns if edit is enabled

        Doesn't need to be overriden, returns the opposite of
        `is_edit_disabled`

        Returns:
            bool: True if edit in GUI is enabled
        """
        return not self.is_edit_disabled()

    @abstractmethod
    def override_disable_edit(self):
        """Disables the PyQt field so the user can't write in it

        For instance, in a `QLineEdit`, the method would call
        `setReadOnly(False)` on it
        """
        pass

    def disable_edit(self):
        """Disables the PyQt field so the user can't write in it

        First checks if disabled
        """
        if not self._disabled:
            self.override_disable_edit()

    def disable(self):
        """Disables the PyQt field so the user can't write in it

        Autoupdate will be also disabled
        """
        if not self._disabled:
            self.disable_edit()
            self.disable_autoupdate()

    @abstractmethod
    def override_enable_edit(self):
        """Enables the PyQt field so the user can write in it

        For instance, in a `QLineEdit`, the method would call
        `setReadOnly(True)` on it
        """
        pass

    def enable_edit(self):
        """Enables the PyQt field so the user can write in it

        First checks if disabled
        """
        if not self._disabled:
            self.override_enable_edit()

    def enable(self):
        """Enables the PyQt field so the user can write in it

        Autoupdate will be also enabled
        """
        if not self._disabled:
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

    def mark_as_not_validated(self, value):
        """Marks the PyQt field as intermediate to the user, modifying it

        Intermediate status is for a field that has not been validated

        Args:
            value (object): value set and not checked against validity
        """
        self._gui_field.setStyleSheet(self.VALIDITY_MARK_SYTLESHEET.format(
            self._gui_field.__class__.__name__,
            self.COLOR_NOT_VALIDATED)
        )

    def mark_as_invalid(self, value, exc):
        """Marks the PyQt field as invalid to the user, modifying it

        Args:
            value (object); value checked as invalid
            exc (Exception): exception triggered so it is marked as invalid
        """
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


class QLineEditBinder(PQSFieldBinder):
    DISABLED_MESSAGE = "<Automatically generated>"

    @property
    def gui_value(self):
        get_value = self._gui_field.text()
        if len(get_value):
            if get_value == self.DISABLED_MESSAGE:
                return None
            else:
                return get_value
        else:
            None

    @gui_value.setter
    def gui_value(self, new_value):
        set_value = new_value
        if new_value is None:
            if self._disabled:
                set_value = self.DISABLED_MESSAGE
            else:
                set_value = ""
        elif not isinstance(new_value, str):
            set_value = str(set_value)
        self._gui_field.setText(set_value)

    @property
    def signal_autoupdate(self):
        return self._gui_field.textChanged

    @property
    def signal_save(self):
        return self._gui_field.returnPressed

    def is_edit_disabled(self):
        return self._gui_field.isReadOnly()

    def override_disable_edit(self):
        self._gui_field.setReadOnly(True)

    def override_enable_edit(self):
        self._gui_field.setReadOnly(False)


class QDateEditBinder(PQSFieldBinder):
    @property
    def gui_value(self):
        return self._gui_field.date().toPyDate()

    @gui_value.setter
    def gui_value(self, new_value):
        if new_value is not None:
            self._gui_field.setDate(new_value)

    @property
    def signal_autoupdate(self):
        return self._gui_field.dateChanged

    def is_edit_disabled(self):
        return self._gui_field.isReadOnly()

    def override_disable_edit(self):
        self._gui_field.setReadOnly(True)

    def override_enable_edit(self):
        self._gui_field.setReadOnly(False)


# # Create widget
class PQSBindersNotValidError(Exception):
    """Binders for GUI fields and model fields are not valid"""
    pass


class PQSBindersNotFoundError(Exception):
    """Binders for GUI fields and model fields can't be found"""
    pass


class PQSSessionNotValidError(Exception):
    """SQLAlchemy session is not valid"""
    pass


class PQSModelNotValidError(Exception):
    """SQLAlchemy model is not valid"""
    pass


class PQSUINotValidError(Exception):
    """UI objects must have a `setupUi` method"""


class PQSFormFieldsNotValidError(Exception):
    """Some fields of the form are not valid"""


class PQSEditUI:
    """Creates a UI to edit a SQLAlchemy data model

    Provides a title, buttons to perform actions and a status bar. The fields
    for user input must be provided in a separate widget.

    Attributes:
        _model (Base): model this UI will help to bind
        _parent (QWidget): widget the UI will be on
        _form_ui (object): holds the input fields of the form
        _binders (list): list of PQSFieldBinder objects that bind inputs to
                         the SQLAlchemy model fields
        _session (sqlalchemy.orm.session.Session): session to track models
    """
    __slots__ = "_model", "_parent", "_form_ui", "_binders", "_session"

    BASE = Base
    """
        object: SQLAlchemy declarative base class in order to check
                subinstances are correct
    """

    SESSION_FACTORY = SESSION_FACTORY
    """
        sqlalchemy.orm.session.sessionmaker: Session factory to create sessions
        if no session is specified
    """

    GUI_BINDERS = {
        "QLineEdit": QLineEditBinder,
        "QDateEdit": QDateEditBinder
    }
    """
        dict: default binders for each QtWidget input field
    """

    def __init__(self, cls_obj, session=None):
        """Initializes the edit UI

        Raises:
            ValueError: some argument has not got a valid type

        Sets the SQLAlchemy model and session. See methods `_set_model` and
        `_set_session` for more information
        """
        self._set_model(cls_obj)
        self._set_session(session)
        self._parent = None
        self._form_ui = None
        self._binders = None

    # Private setters
    def _set_model(self, model_cls_obj):
        """Sets the SQLAlchemy model to bind to the GUI

        Detects if the passed argument is a class or an object in order to
        create a new model from the class or use the existing model passed

        If no valid model is passed, raises ValueError

        Raises:
            ValueError: if passed argument is not either a valid SQLAlchemy
                        model object (subinstance of self.BASE) or class
                        (subclass of self.BASE)

        Args:
            model_cls_obj (mixed): the SQLAlchemy model class / object to bind
                if it's an object, will bind this model and display its values
                if it's a class, will create a new empty object from it
        """
        # Create or save model
        if inspect.isclass(model_cls_obj):
            # Detect if class is correct
            if issubclass(model_cls_obj, self.BASE):
                self._model = model_cls_obj()
            else:
                raise PQSModelNotValidError("Model must be a class based on " +
                                            "SQLAlchemy's base class")
        elif isinstance(model_cls_obj, Base):
            # The passed value is an object
            self._model = model_cls_obj
        else:
            # No valid model passed
            raise PQSModelNotValidError(
                "Model must be a subclass of SQLAlchemy's base class or an " +
                "instance of a subclass of it")

    def _set_session(self, session):
        """Sets the SQLAlchemy session to use in the binder

        Must be either a sqlalchemy.orm.session.Session object or None so we
        can create a new session using the session maker stored

        Raises:
            ValueError: if session passed is not valid

        Args:
            session (sqlalchemy.orm.session.Session): session to track model
                will create one if empty
        """
        # Create or save session
        if session is None:
            self._session = self.SESSION_FACTORY()
        elif isinstance(session, Session):
            # The passed value is an object
            self._session = session
        else:
            # No valid model passed
            raise PQSSessionNotValidError(
                "Session must be an instance of SQLAlchemy's " +
                "`sqlalchemy.orm.session.Session` or `None` to create one " +
                "automatically")

    # Generic properties
    @property
    def binders(self):
        """Returns the binders list"""
        return self._binders

    @binders.setter
    def binders(self, binders):
        """Sets the field binders. Just can be set if not set before

        Validates them previous to set them. May raise an exception if not
        valid. See `validate_binders` method
        """
        if self._binders is None:
            self.validate_binders(binders)
            self._binders = binders

    @property
    def form_widget(self):
        """Returns the widget where the field inputs must be present"""
        return self.formWidget

    @property
    def form_ui(self):
        """Returns the UI object that holds the form input fields"""
        return self._form_ui

    @property
    def model(self):
        """Returns SQLAlchemy binded model"""
        return self._model

    @property
    def parent(self):
        """Returns parent QWidget. Doesn't exist before calling `setupUi`"""
        return self._parent

    @property
    def session(self):
        """Returns SQLAlchemy session"""
        return self._session

    # UI methods
    # # Properties
    @property
    def save_button(self):
        """Returns the `QPushButton` to press to save values"""
        return self.saveButton

    @property
    def validate_button(self):
        """Returns the `QPushButton` to press to validate values"""
        return self.validateButton

    @property
    def refresh_button(self):
        """Returns the `QPushButton` to press to refresh values"""
        return self.refreshButton

    @property
    def delete_button(self):
        """Returns the `QPushButton` to press to delete the record"""
        return self.deleteButton

    @property
    def status_label(self):
        """Returns the `QLabel` where status message is set"""
        return self.statusLabel

    # # Setup
    def setup_and_bind(self, parent, form_ui):
        """Sets up the UI and afterwards the form UI, binding to it

        Notes:
            May rise one of the `bind_form` exceptions
        """
        self.setupUi(parent)
        self.bind_form(form_ui)

    @abstractmethod
    def setupUi(self, parent):
        """Sets up the UI depending on the design

        Default behaviour is just to call parent `setupUi` and save parent
        `QWidget`
        """
        self._parent = parent
        super().setupUi(parent)

    # # Bind edit form with input fields form
    # # # Binders
    @classmethod
    def validate_binders(binders):
        """Given a list of field binders, validates if they are binders

        Raises:
            PQSBindersNotValidError: if a binder is not valid

        Args:
            binders (list): supposed list of PQSFieldBinder objects
        """
        for binder in binders:
            if not isinstance(binder, PQSFieldBinder):
                raise PQSBindersNotValidError(
                    "Binders were found in `form_ui` but they were not " +
                    "subinstances of `PQSFieldBinder`")

    def lookup_binders(self):
        """Tries to get the binders or guess them from `form_ui`

        First, checks if binders are already set. If that's the case, does
        nothing.

        Then, checks if the passed `form_ui` has the member `binders`. If it
        is found, it is saved as the `binders` list. It's on behalf of the
        `form_ui` class to have listed the `binders` properly. The method will
        check if they are instances os `PQSFieldBinder` just in case.

        If no `binders` attribute can be found, `binders` are automatically
        generated using default binders for each type of user input. The names
        to map to the model are obtained from the attribute names, removing the
        type prefix (ie: LineEdit, DateEdit, ...).

        Raises:
            PQSBindersNotValidError: if binders found are not valid
            PQSBindersNotFoundError: if no binders can be found after looking
                in form and guessing
        """
        # 1. Are already binders set?
        if self._binders is not None:
            return
        # 2. Get binders directly
        binders = getattr(self._form_ui, "binders", None)
        if binders is not None:
            # Check if binders are binders
            self.validate_binders(binders)
            # Save them
            self._binders = binders
        # 3. Guess them
        self._binders = []
        for attr_name in dir(self._form_ui):
            # Get attribute and its class
            attr = getattr(self._form_ui, attr_name)
            attr_class_name = attr.__class__.__name__
            # Check if class has default binder
            if attr_class_name in self.GUI_BINDERS:
                # Try to guess name
                field_suffix = attr_class_name[1:]
                name = attr_name.replace(field_suffix, "")
                # Check if name exists
                name_exists = True
                try:
                    getattr(self._model, name)
                except Exception as e:
                    name_exists = False
                # Add to binders if exists
                if name_exists:
                        self._binders.append(
                            self.GUI_BINDERS[attr_class_name](
                                attr, self, name))
        # n. Can't find them
        if not len(self._binders):
            raise PQSBindersNotFoundError(
                "Binders couldn't be found or guessed, your UI is not " +
                "backed from / to any model")

    # # # Form binder
    def bind_form(self, form_ui):
        """Binds the form UI into the edit UI

        Will also lookup for binders. So it can raise any `lookup_binders`
        exception

        Raises:
            PQSUINotValidError: if UI doesn't have `setupUi` mandatory method

        Args:
            form_ui (object): UI that adds input fields (QWidgets)
                              can be a class, therefore we'll create the object
                              it can be a UI created compiling a `.ui` file
        """
        # Detect if valid class / object
        if not callable(getattr(form_ui, "setupUi", None)):
            raise PQSUINotValidError("form_ui must have a setupUi method")
        # Create object if it's a class
        self._form_ui = form_ui() if inspect.isclass(form_ui) else form_ui
        # Setup form UI
        try:
            self._form_ui.setupUi(self.form_widget)
        except Exception as e:
            raise PQSUINotValidError("Unable to call `setupUi`:", str(e))
        # Lookup binders
        self.lookup_binders()
        # Fill GUI
        self.update_to_gui()
        # Validate if they're not clean
        for binder in self._binders:
            # Validate if not persistent and clean
            status = sqla_inspect(self.model)
            if status.persistent and not status.modified:
                self.update_status()
            else:
                binder.update()
        # Attach events
        self.attach_events()

    # # # Updaters from / to GUI to / from model
    def update_from_gui(self):
        """Tries to set all GUI fields into the model

        They will be validated before being set, triggering validation errors
        if needed
        """
        for binder in self._binders:
            binder.disable_edit()
            binder.update()
            binder.enable_edit()

    def update_to_gui(self, skip_validate=False):
        """Sets all model fields into the GUI

        Will be marked as not validated by default.

        Args:
            skip_validate (bool): True to skip validate, set as not validated
        """
        for binder in self._binders:
            binder.disable()
            binder.update_to_gui()
            if skip_validate:
                binder.mark_as_not_validated(binder.model_value)
            else:
                binder.update()
            binder.enable()

    # # # Events attaching
    def attach_events(self):
        """Attaches the edit UI events to their event handlers

        Uses properties to retrieve the correct buttons
        """
        self.save_button.clicked.connect(self._on_save)
        self.refresh_button.clicked.connect(self._on_refresh)
        self.validate_button.clicked.connect(self._on_validate)
        self.delete_button.clicked.connect(self._on_delete)

    # # # Actions
    def save(self):
        """Saves the requested changes

        If requested to delete, commits the deletion, if not proceeds to save
        new changes.

        First tries to set all GUI values into the model, afterwards, if all
        values could be set, tries to commit the changes using SQLAlchemy

        Notes:
            May also rise some of the `commit` method exceptions

        Raises:
            PQSFormFieldsNotValidError: some of the form fields are not valid
            model couldn't be updated so commit was not performed
        """
        # DELETE MODE
        status = sqla_inspect(self._model)
        if status.deleted:
            self.commit()
            return
        # ADD / EDIT MODE
        # # Check if ALL fields are valid
        fields_are_valid = True
        for binder in self._binders:
            if not binder.update():
                fields_are_valid = False
        # # Add and commit if valid
        if fields_are_valid:
            self._session.add(self._model)  # idempotent, can do it `n` times
            self.commit()
        else:
            raise PQSFormFieldsNotValidError(
                "Some fields were not valid, could not commit")

    def commit(self):
        """Adds the model to the session and commits

        Rollsback if necessary

        Raises:
            Exception: SQLAlchemy exceptions on `commit` or `rollback`
        """
        # Commit
        rollback = False
        try:
            self._session.commit()
        except Exception as e:
            rollback = True
        # Rollback if necessary
        if rollback:
            self._session.rollback()
        else:
            # Reload values into GUI (autocalculated values)
            self.update_to_gui(True)
        # Update status
        self.update_status()

    def validate(self):
        """Alias of `update_from_gui`, trying to update the model validates"""
        self.update_to_gui(False)

    def refresh(self):
        """Refreshes the model from the backend and displays its values

        Fields won't be validated upon request, so no pending changes are set

        Updates edit UI status afterwards

        Raises:
            Exception: SQLAlchemy `refresh` method can raise exceptions
        """
        # If deleted, undo delete
        if sqla_inspect(self._model).deleted:
            self._session.rollback()
        # Refresh
        self._session.refresh(self._model)
        self.update_to_gui(True)
        self.update_status()

    def delete(self):
        """Deletes the model from the session and commits

        Rollsback if necessary

        Raises:
            Exception: SQLAlchemy exceptions on `commit` or `rollback`
        """
        # Delete
        self._session.delete(self._model)
        self._session.flush()
        # Update status
        self.update_status()

    def update_status(self):
        """Updates the status message depending on SQLAlchemy model status

        Executes event handlers for each status
        """
        stat = sqla_inspect(self.model)
        if stat.transient:
            self._on_status_transient()
        elif stat.pending:
            self._on_status_pending()
        elif stat.persistent:
            self._on_status_persistent()
            if stat.modified:
                self._on_status_persistent_modified()
            else:
                self._on_status_persistent_unmodified()
        elif stat.deleted:
            self._on_status_deleted()
        elif stat.detached:
            self._on_status_detached()

    # # # Events handlers
    def _on_save(self):
        """Triggers when wanting to save the record changes

        Default is to call `save`
        """
        self.save()

    def _on_commit(self):
        """Triggers when wanting to commit the record changes

        Default is to call `commit`
        """
        self.commit()

    def _on_validate(self):
        """Triggers when wanting to validate the record fields

        Default is to call `validate`
        """
        self.validate()

    def _on_refresh(self):
        """Triggers when wanting to refresh the record fields

        Default is to call `refresh`
        """
        self.refresh()

    def _on_delete(self):
        """Triggers when wanting to delete the record

        Needs confirmation (save trigger). Default is to call `delete`
        """
        self.delete()

    def _on_status_transient(self):
        """Triggered when the model status is transient"""
        self.save_button.show()
        self.validate_button.show()
        self.refresh_button.hide()
        self.delete_button.hide()
        self.status_label.setText(
            "Transient (not tracked)")

    def _on_status_pending(self):
        """Triggered when the model status is pending"""
        self.save_button.show()
        self.validate_butotn.show()
        self.refresh_button.hide()
        self.delete_button.hide()
        self.status_label.setText(
            "Pending (tracked but pending to add to database)")

    def _on_status_persistent(self):
        """Triggered when the model status is persistent"""
        self.save_button.show()
        self.validate_button.show()
        self.refresh_button.show()
        self.delete_button.show()
        self.status_label.setText(
            "Persistent (tracked and present in database)\n")

    def _on_status_persistent_modified(self):
        """Triggered when the model status is persistent and changes pending"""
        self.status_label.setText(
            self.status_label.text() +
            "Some changes are pending to be commited")

    def _on_status_persistent_unmodified(self):
        """Triggered when the model status is persistent, no changes pending"""
        self.status_label.setText(
            self.status_label.text() +
            "No new changes to be commited")

    def _on_status_deleted(self):
        """Triggered when the model status is deleted

        Delete is pending, but has not been commited yet
        """
        self.save_button.show()
        self.validate_button.show()
        self.refresh_button.show()
        self.delete_button.hide()
        self.status_label.setText(
            "Deleted (pending to delete from the database)\n")

    def _on_status_detached(self):
        """Triggered when the model status is detached

        Delete has been performed, model is not in the database now.ABCMeta

        Disables write so user can't do anything from now
        """
        for binder in self._binders:
            binder.disable()
        self.save_button.hide()
        self.refresh_button.hide()
        self.validate_button.hide()
        self.delete_button.hide()
        self.status_label.setText(
            "Detached (deleted from the database)")


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
    SESSION_FACTORY = sessionmaker(bind=engine)
    PQSEditUI.SESSION_FACTORY = SESSION_FACTORY
    # # Qt
    app = QApplication(sys.argv)
    widget = QWidget()
    print("ui mode: %s" % mode)
    edit_ui = type("CustomEditUI", (PQSEditUI, Ui_PQSEditUI), {})
    if mode == "add":
        ui = edit_ui(User)
    elif mode == "edit-transient":
        ui = edit_ui(User(email="transient@users.org", number=1))
    elif mode == "edit-pending":
        u = User(email="pending@users.org", number=2)
        s = SESSION_FACTORY()
        s.add(u)
        ui = edit_ui(u, s)
    elif mode == "edit-persistent":
        u = User(email="persistent@users.org", number=3,
                 birthdate=datetime.date(1995, 9, 21))
        s = SESSION_FACTORY()
        s.add(u)
        s.commit()
        ui = edit_ui(u, s)
    elif mode == "edit-persistent-wrong":
        s = SESSION_FACTORY()
        s.execute("INSERT INTO users (email, number, birthdate) VALUES (" +
                  "\"persistent-wrongusers.org\", 4, \"2099-12-12\")")
        s.commit()
        u = s.query(User).first()
        ui = edit_ui(u, s)
    ui.setup_and_bind(widget, Ui_UserForm)
    widget.show()
    # run and show
    sys.exit(app.exec_())
