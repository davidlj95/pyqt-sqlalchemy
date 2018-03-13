"""Defines a PQSConnectUI

The PQSConnectUI allows to define a UI so the settings of the SQLAlchemy
engine can be set via a GUI using Qt. You can create a subclass that defines
the real Qt UI and the class will handle trying to create the engine and
triggering the events according to the result (fail, success).

The default one also closes the window and binds the `SessionMaker` engine
with the created engine (if created succesfully)
"""
# Libraries
# # Internal
from .start import bind_engine
# # External
from PyQt5.QtWidgets import QLineEdit
from sqlalchemy import create_engine


class PQSConnectUI():
    """Allows to graphically create a new engine to connect to a database

    Just pass the known parameters and the class will generate the correct
    URL for it. Also, will test upon finished if the connection succeeds and
    if that's the case, will set the SessionFactory engine with the engine
    retrieved.

    The UI must construct input fields for the connector, host, user, password,
    port and database. Those input fields will be `QLineEdit` to make things
    easier.

    Just tested with MySQL connector.

    Attributes:
        _connector (str): connector to use to connect to the database
        _username (str): username to use to connect to the database
        _password (str): password to use to connect to the database
        _host (str): host to connect to the database
        _port (str): port to connecto to the database
        _database (str): database name to connect to
        _opts (bool): other opts to pass when creating the engine
    """
    __slots__ = ["_connector", "_username", "_password", "_host", "_port",
                 "_database", "_opts"]

    # Initializer
    def __init__(self, connector=None, username=None, password=None, host=None,
                 port=None, database=None, opts={}):
        self._connector = connector
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._database = database
        self._opts = opts

    # Model properties
    @property
    def connector(self):
        """Returns the connector defined or the UI value if not defined"""
        return self.connector_input_value if self._connector is None else \
            self._connector

    @property
    def connector_input(self):
        """Returns the connector GUI object"""
        return self.connectorLineEdit

    @property
    def connector_input_value(self):
        """Returns the connector set in the UI"""
        return self.connector_input.text()

    @property
    def username(self):
        """Returns the username defined or the UI value if not defined"""
        return self.username_input_value if self._username is None else \
            self._username

    @property
    def username_input(self):
        """Returns the username GUI object"""
        return self.usernameLineEdit

    @property
    def username_input_value(self):
        """Returns the username set in the UI"""
        return self.username_input.text()

    @property
    def password(self):
        """Returns the password defined or the UI value if not defined"""
        return self.password_input_value if self._password is None else \
            self._password

    @property
    def password_input(self):
        """Returns the password GUI object"""
        return self.passwordLineEdit

    @property
    def password_input_value(self):
        """Returns the password set in the UI"""
        return self.password_input.text()

    @property
    def host(self):
        """Returns the host defined or the UI value if not defined"""
        return self.hostLineEdit.text() if self._host is None else \
            self._host

    @property
    def host_input(self):
        """Returns the host GUI object"""
        return self.hostLineEdit

    @property
    def host_input_value(self):
        """Returns the host set in the UI"""
        return self.host_input.text()

    @property
    def port(self):
        """Returns the port defined or the UI value if not defined"""
        return self.port_input_value if self._port is None else \
            self._port

    @property
    def port_input(self):
        """Returns the port GUI object"""
        return self.portLineEdit

    @property
    def port_input_value(self):
        """Returns the port set in the UI"""
        return self.port_input.text()

    @property
    def database(self):
        """Returns the database defined or the UI value if not defined"""
        return self.database_input_value if self._database is None else \
            self._database

    @property
    def database_input(self):
        """Returns the database GUI object"""
        return self.databaseLineEdit

    @property
    def database_input_value(self):
        """Returns the database set in the UI"""
        return self.database_input.text()

    @property
    def connect_button(self):
        """Connect button GUI object"""
        return self.connectButton

    @property
    def uri(self):
        """Returns the connection URI based on the defined information"""
        return "{0}://{1}:{2}@{3}:{4}/{5}".format(
            self.connector, self.username, self.password, self.host, self.port,
            self.database)

    # UI setup
    def setupUi(self, parent):
        """Creates the form elements

        Also attaches events and hides unnecesary fields
        """
        self.parent = parent
        if callable(getattr(super(), "setupUi", None)):
            super().setupUi(parent)
        self.attach_events()
        self.hide_fields()

    def hide_fields(self):
        """Hide fields whose values have been set at init time"""
        if self._connector is not None:
            self.connector_input.hide()
            if getattr(self, "connectorLabel", None):
                self.connectorLabel.hide()
        if self._username is not None:
            self.username_input.hide()
            if getattr(self, "usernameLabel", None):
                self.usernameLabel.hide()
        if self._password is not None:
            self.password_input.hide()
            if getattr(self, "passwordLabel", None):
                self.passwordLabel.hide()
        if self._host is not None:
            self.host_input.hide()
            if getattr(self, "hostLabel", None):
                self.hostLabel.hide()
        if self._port is not None:
            self.port_input.hide()
            if getattr(self, "portLabel", None):
                self.portLabel.hide()
        if self._database is not None:
            self.database_input.hide()
            if getattr(self, "databaseLabel", None):
                self.databaseLabel.hide()
        # If everything is set, create connection
        if self._connector is not None and self._username is not None and \
            self._password is not None and self._host is not None and \
                self._port is not None and self._database is not None:
            self.create()

    # Event attacher
    def attach_events(self):
        """Attach events to their handlers"""
        # Text on return
        if isinstance(self.connector_input, QLineEdit):
            self.connectorLineEdit.returnPressed.connect(self.create)
        if isinstance(self.username_input, QLineEdit):
            self.username_input.returnPressed.connect(self.create)
        if isinstance(self.password_input, QLineEdit):
            self.password_input.returnPressed.connect(self.create)
        if isinstance(self.host_input, QLineEdit):
            self.host_input.returnPressed.connect(self.create)
        if isinstance(self.port_input, QLineEdit):
            self.port_input.returnPressed.connect(self.create)
        if isinstance(self.database_input, QLineEdit):
            self.database_input.returnPressed.connect(self.create)
        # Connect button
        self.connect_button.clicked.connect(self.create)

    # Actions
    def create(self):
        """Creates an engine and tries to connnect to it"""
        # Create engine
        uri = self.uri
        engine = create_engine(uri, **self._opts)
        # Try to connect
        try:
            c = engine.connect()
        except Exception as exc:
            self._on_create_failed(uri, exc)
        else:
            c.close()
            self._on_create_success(uri, engine)
        finally:
            self._on_create(uri)

    def _on_create(self, uri):
        """Triggers when fails or succeeds connecting to the engine

        Args:
            uri (str): uri the engine was trying to be connected to
        """
        self.on_create(uri)

    def _on_create_failed(self, uri, exc):
        """Triggered when fails to connect to the engine

        Args:
            exc (Exception): exception raised
            uri (str): uri the engine was trying to be connected to
        """
        self.on_create_failed(uri, exc)

    def _on_create_success(self, uri, engine):
        """Triggered when succeeds to connect to the engine

        Default is to close window

        Args:
            uri (str): uri the engine was connected to
            engine (sqlalchemy.engine.Engine): engine created
        """
        self.on_create_success(uri, engine)

    # Custom event handler
    def on_create_success(self, uri, engine):
        """Triggered when succeeds to connect to the engine

        Can be overriden by the user
        """
        pass

    def on_create_failed(self, uri, engine):
        """Triggered when fails to connect to the engine

        Can be overriden by the user
        """
        pass

    def on_create(self, uri):
        """Triggered when tried to connect to the engine.ABCMeta

        Can be overriden by the user
        """
        pass


class PQSConnectDefaultUI(PQSConnectUI):
    """Same as PQSConnectUI but when success, sets the default engine

    Uses the `start` module to bind the engine automatically to the
    `SessionMaker` if the connection succeeds
    """
    def _on_create_success(self, uri, engine):
        """Closes the window and sets the engine in `SessionMaker`

        Needs parent QWidget to be saved on `parent`
        """
        bind_engine(engine)
        self.parent.close()
        super()._on_create_success(uri, engine)
