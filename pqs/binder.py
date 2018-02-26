"""Defines a PQS base binder

A binder in PQS is a class that binds an SQLAlchemy model's field to a PyQt
user input widget, allowing to access both of them through it and update it
using the model's value or the user input's value.

Not just that, the binder also can provide the `autoupdate` feature, meaning
that upon a user input change signal is triggered, the model will be updated
automatically with this value. If the model has a SQLAlchemy model validator,
it can also display visually if the value was updated to the model or not.

This is the base so the `PQSEditUI` can perform its actions without knowing
the relationships of the input fields and their model values, it just needs the
binder that joins and allows access to both.
"""
# Libraries
# # Built-in
from abc import ABCMeta, abstractmethod


# Classes
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
