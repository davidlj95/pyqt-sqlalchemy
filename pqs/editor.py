"""Defines the metaclass of a PQS Edit UI

The PQSEditUI defines a UI that controls some graphical user inputs, that are
binded to a model and allows to perform actions on the model once the user has
edited those inputs.

The design of the UI that holds user inputs and actions buttons has to be
created using a tool like `QtCreator`. The method `setupUi` must therefore
build those action buttons and a `QWidget` where the user input fields will
be placed.

The usage is the following:
    1) The PQSEditUI is inherited by a class that defines a `setupUi` method
       It must define a save, refresh, validate and delete button and a status
       label. They must be named `saveButton`, `refreshButton`,
       `validateButton`, `deleteButton` and `statusLabel` respectively.

       They can be named different if the properties that access them are
       overriden.

    2) When this class is initialized, `PQSEditUi` needs the SQLAlchemy model
       that it will be editing and the session where this model will be added
       or removed, or commit when necessary. You can pass the model class so
       an empty GUI is set to create a new record or an existing one to edit
       it. See `_set_model` and `_set_session` for more information

    3) After the class is initialized, you must call `setup_and_bind` method,
       passing it a form UI class (has a `setupUi` method). Then the edit UI is
       built and the user inputs defined in the form UI passed are added to the
       form widget in the edit UI.

       What we described is the `setup`, then the `bind` is performed. The bind
       operation is the one that will look for binders so the user input fields
       in the UI are mapped to the model. The form UI must define this binders
       as a list so they are accessible by the `binders` attribute or they will
       be guessed and created using the default binders and the names of the
       input fields objects to find what they are mapping. See `bind_form` for
       more information

    4) You can just add a new record from the model or edit an existing one
       (depending if you passed an empty object or the model class or an
       existing object)
"""
# Libraries
# # Built-in
import inspect
from abc import ABCMeta, abstractmethod
# # Internal
from .start import SessionFactory, Base
from .errors import PQSUINotValidError, PQSModelNotValidError, \
                    PQSBindersNotFoundError, PQSBindersNotValidError, \
                    PQSFormFieldsNotValidError, PQSSessionNotValidError
from .binder import PQSFieldBinder
from .binders_sample import QLineEditBinder, QDateEditBinder
# # External
from sqlalchemy import inspect as sqla_inspect
from sqlalchemy.orm import Session


# Classes
class PQSEditUI(metaclass=ABCMeta):
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

    SESSION_FACTORY = SessionFactory
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
        self.update_to_gui(True)
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
        self.validate_button.show()
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
