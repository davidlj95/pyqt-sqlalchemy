"""Defines the class to be able to query SQLAlchemy models graphically

To query a model, we need a UI to specify some filters and also a `QTableView`
object to display the results there.

This `QTableView` needs a data model so the contents can be displayed properly

The first problem is solved by the `PQSQueryUI` class, that helps controlling
a query UI with a column selection as a filter, operator selection to filter,
and a filter value. Then, has a `QTableView` to display results.abs

The second problem, the data model, is specified by the `PQSTableModel` class
that allows to display results from a SQLAlchemy query in a `QTableView` by
implementing a `QAbstractTableModel`
"""
# Libraries
# # Internal
from .helpers import get_session, get_model_class, get_model_columns_names
# # External
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, QAbstractTableModel


class PQSTableModel(QAbstractTableModel):
    """Defines a Qt QAbstractTable model suitable to work with SQLAlchemy

    Attributes:
        _model (start.Base): SQLAlchemy model to query
        _session (sqlalchemy.session.Session): session to use to query
        _query (sqlalchemy.orm.query.Query): query to perform to get results
        _columns (list): list of columns names to display in table
        _sort_column (int): number of column to sort, None to don't sort
        _sort_order (Qt.SortOrder): order descending or ascending
        _limit (int): maximum number of results
        _results (list): list of SQLAlchemy result objects
    """
    __slots__ = "_model", "_session", "_query", "_columns", "_sort_column", \
                "_sort_order", "_limit", "_results"

    DEFAULTS_COLUMNS = None
    """
        list(str): default list of columns to display in the results
                   None means they will be all of them found automatically
    """
    DEFAULT_SORT_COLUMN = 0
    """
        int: number of column (in the list of columns) to sort by default
    """
    DEFAULT_SORT_ORDER = Qt.AscendingOrder
    """
        Qt.SortOrder: default sort order if not specified
    """
    DEFAULT_LIMIT = 250
    """
        int: default safe limit to avoid large result sets
    """

    # Initialization
    def __init__(self, model, session, query=None, columns=DEFAULTS_COLUMNS,
                 sort_column=DEFAULT_SORT_COLUMN,
                 sort_order=DEFAULT_SORT_ORDER,
                 limit=DEFAULT_LIMIT):
        """Initializes a PQSTableModel

        Sets the specified parameters as specified in the class attributes

        Args:
            _model (start.Base): SQLAlchemy model to query
            _session (sqlalchemy.session.Session): session to use to query
            _query (sqlalchemy.orm.query.Query): query to perform to get result
            _columns (list): list of columns names to display in table
            _sort_column (int): number of column to sort, None to don't sort
            _sort_order (Qt.SortOrder): order descending or ascending
            _limit (int): maximum number of results
        """
        super().__init__()
        self._model = get_model_class(model)
        self._session = get_session(session)
        self._query = query
        self._columns = columns \
            if columns is not None else get_model_columns_names(self._model)
        self._sort_column = sort_column
        self._sort_order = sort_order
        self._limit = limit
        self._results = None

    # Properties
    @property
    def model(self):
        """SQLAlchemy model we are displaying"""
        return self._model

    @property
    def session(self):
        """Returns the session that controls the model relation to the DB"""
        return self._session

    @property
    def query(self):
        """Returns the query being performed"""
        return self._query

    @query.setter
    def query(self, new_query):
        """Sets the query to retrieve results from"""
        self._query = new_query

    @property
    def columns(self):
        """Returns the list of columns of the table"""
        return self._columns

    @property
    def sort_column(self):
        """Returns the column to sort, None if no order applies"""
        return self._sort_column

    @property
    def sort_order(self):
        """Returns the sort order, ascending by default"""
        return self._sort_order

    @property
    def limit(self):
        """Maximum number of items to query for. None for unlimited"""
        return self._limit

    @property
    def results(self):
        """SQLAlchemy results of the query so they can be displayed"""
        return self._results

    # Qt Overrides
    def columnCount(self, parent):
        """QtOverride: number of columns"""
        return len(self._columns)

    def rowCount(self, parent):
        """QtOverride: number of rows (results)"""
        return len(self._results) if self._results is not None else 0

    def headerData(self, column_num, orientation, role):
        """QtOverride: asks for header data based on col, orientation and role

        Args:
            column_num (int): number of the column to set header
            orientation (Qt.Orientation):
        """
        # Column names
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._columns[column_num]

    def flags(self, index):
        """QtOverride: abilities of the model"""
        return Qt.NoItemFlags

    def supportedDropActions(self):
        """QtOverride: abilities to drop"""
        return Qt.IgnoreAction

    def supportedDragActions(self):
        """QtOverride: abilities to drag

        Default is what `supportedDropActions` returns"""
        return self.supportedDropActions()

    def dropMimeData(self, data, action, row, col, parent):
        """QtOverride: data supplied by a drag and drop

        If returns False, operation failed
        """
        return False

    def data(self, index, role):
        """QtOverride: asks for data in the index with that role"""
        if index.isValid() and role == Qt.DisplayRole:
            row = self._results[index.row()]
            name = self._columns[index.column()]
            return str(getattr(row, name))

    def sort(self, col, order):
        """QtOverride: sort table by given column number"""
        self._sort_column = col
        self._sort_order = order
        self.refresh()

    # Retrieving results
    def refresh(self):
        """Refreshes the data querying the database"""
        # Check a query is available
        if self.query is None:
            return

        # We are going to change things
        self.layoutAboutToBeChanged.emit()

        # Retrieve query
        query = self._query

        # # Sort
        if self._sort_column is not None:
            column = getattr(self._model, self._columns[self._sort_column])
            if self._sort_order == Qt.DescendingOrder:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)

        # # Limit
        if isinstance(self._limit, int):
            query = query.limit(self._limit)

        # Do the query
        try:
            results = query.all()
        except Exception as exc:
            self._on_refresh_failed(query, exc)
        else:
            self._results = results
            self._on_refresh_success(query, results)
        finally:
            self._on_refresh(query)

        # Changed layout
        self.layoutChanged.emit()

    # Events (class)
    def _on_refresh(self, query):
        """Triggered when refreshed, either success or failed"""
        self.on_refresh(query)

    def _on_refresh_success(self, query, results):
        """Triggered when refresh succeeds, passes query and results"""
        self.on_refresh_success(query, results)

    def _on_refresh_failed(self, query, exc):
        """Triggered when refresh fails, passes query and exception"""
        self.on_refresh_failed(query, exc)

    # Events (user)
    def on_refresh(self, query):
        """Triggered when refreshed, either success or failed

        Customizable by the class user
        """
        pass

    def on_refresh_success(self, query, results):
        """Triggered when refresh succeeds, passes query and results

        Customizable by the class user
        """
        pass

    def on_refresh_failed(self, query, exc):
        """Triggered when refresh fails, passes query and exception

        Customizable by the class user
        """
        pass


class PQSOperator(type):
    """Defines a SQLAlchemy operator to use as filter in queries

    Each SQLAlchemy operator will have an `id` so they can be used in
    `QComboBox`es and be listed and retrieved through this list, a `name` to
    display the operator to the user and finally, the operator name that
    allows to pick it dynamically from one of the list available in
        `sqlalchemy.sql.operators.ColumnOperators`

    This metaclass of all operators allows to keep an automatic register of
    all operators so they can be automatically retrieved
    """
    map_by_name = {}
    """
        dict: maps the name of the operator (its class name) to their class
    """
    listing = []
    """
        list: lists all the defined operators
    """

    def __new__(cls, name, bases, attrs):
        """Creates a new PQSOperator and adds it to the register"""
        # Create
        new_cls = super(PQSOperator, cls).__new__(cls, name, bases, attrs)
        # Get ID, the last element of the list
        list_len = len(PQSOperator.listing)
        # Append and set id
        PQSOperator.listing.append(new_cls)
        new_cls.id = list_len
        # Map by name too
        PQSOperator.map_by_name[new_cls.__name__] = new_cls
        # Create class
        return new_cls


class PQSOperatorLike(metaclass=PQSOperator):
    """PQSOperator that compares using LIKE operator (case-sensitive)"""
    name = "~="
    operator = "like"


class PQSOperatorILike(metaclass=PQSOperator):
    """PQSOperator that compares using ILIKE operator (case-insensitive)"""
    name = "~= (Aa)"
    operator = "ilike"


class PQSOperatorEquals(metaclass=PQSOperator):
    """PQSOperator that compares using == operator"""
    name = "=="
    operator = "__eq__"


class PQSOperatorNotEquals(metaclass=PQSOperator):
    """PQSOperator that compares using != operator"""
    name = "!="
    operator = "__ne__"


class PQSOperatorGreater(metaclass=PQSOperator):
    """PQSOperator that compares using > operator"""
    name = ">"
    operator = "__gt__"


class PQSOperatorGreaterEquals(metaclass=PQSOperator):
    """PQSOperator that compares using >= operator"""
    name = ">="
    operator = "__ge__"


class PQSOperatorLess(metaclass=PQSOperator):
    """PQSOperator that compares using < operator"""
    name = "<"
    operator = "__lt__"


class PQSOperatorLessEquals(metaclass=PQSOperator):
    """PQSOperator that compares using <= operator"""
    name = "<="
    operator = "__le__"


class PQSOperatorContains(metaclass=PQSOperator):
    """PQSOperator that compares using IN operator"""
    name = "c"
    operator = "in_"


class PQSOperatorNotContains(metaclass=PQSOperator):
    """PQSOperator that compares using NOT IN operator"""
    name = "nc"
    operator = "notin_"


class PQSOperatorIsNull(metaclass=PQSOperator):
    """PQSOperator that compares using IS NULL operator"""
    name = "=0"
    operator = "is_"


class PQSOperatorIsNotNull(metaclass=PQSOperator):
    """PQSOperator that compares using IS NOT NULL operator"""
    name = "!=0"
    operator = "isnot"


class PQSQueryUI():
    """Main GUI to query any SQLAlchemy model

    The specific UI is let to be designed separately

    Attributes:
        _model (Base): SQLAlchemy model to lookup
        _session (sqlalchemy.session.Session): session to use to lookup
        _table_model (PQSTableModel): table model to use to display results
        _sorting_enabled (bool): true to allow sorting by column
        _columns (list(str)): columns of the model
        _column_query (int): column number of the columns list that will be
                             used to query by default if no column is specified
    """
    __slots__ = "_model", "_session", "_table_model", "_sorting_enabled", \
                "_columns", "_column_query"
    DEFAULT_TABLE_MODEL = PQSTableModel
    """
        QAbstractTableModel: table model to use to display results
    """
    DEFAULT_SORTING_ENABLED = True
    """
        bool: control whether new QueryUI can sort by default
    """
    DEFAULT_COLUMN_QUERY = 0
    """
        int: default column to query
    """
    # Initialization
    def __init__(self, model, session=None, table_model=DEFAULT_TABLE_MODEL,
                 sorting_enabled=DEFAULT_SORTING_ENABLED,
                 column_query=DEFAULT_COLUMN_QUERY):
        """Initializes a PQSQueryUI

        Sets the main class attributes, defaulting others.

        Args:
            _model (Base): SQLAlchemy model to lookup
            _session (sqlalchemy.session.Session): session to use to lookup
            _table_model (PQSTableModel): table model to use to display results
            _sorting_enabled (bool): true to allow sorting by column
            _column_query (int/str): name or id of the column to search by
                                     default
        """
        # Mandatories
        self._model = get_model_class(model)
        self._columns = get_model_columns_names(self._model)
        self._session = get_session(session)
        self._table_model = table_model \
            if isinstance(table_model, PQSTableModel) \
            else table_model(self._model, self._session)
        # Optionals
        self._sorting_enabled = sorting_enabled
        if isinstance(column_query, int):
            assert 0 <= column_query < len(self._columns), "column to " + \
                "query, if specified as id (int) has to be in the range " + \
                "of number of columns for the model %s (%d)" % (
                    self._model.__name__, len(self._columns))
            self._column_query = column_query
        elif isinstance(column_query, str):
            try:
                column_query = self._columns.index(column_query)
            except Exception as e:
                raise AssertionError(
                    "column to query specified (%s) is valid for model %s. " +
                    "Model columns are %s" % (
                        column_query, self._model.__name__, self._columns))
            else:
                self._column_query = column_query

    # Properties
    @property
    def model(self):
        """Returns the SQLAlchemy model to be queried"""
        return self._model

    @property
    def session(self):
        """Returns the SQLAlchemy session to use to query"""
        return self._model

    @property
    def query(self):
        """Creates the SQLAlchemy query based on the form values"""
        return self.generate_query()

    @property
    def table_model(self):
        """Returns the table model used to display results"""
        return self._table_model

    @property
    def columns(self):
        """Returns the columns of the model"""
        return self._columns

    @property
    def sorting_enabled(self):
        """Returns whether sorting is enabled"""
        return self.results_table.isSortingEnabled()

    @sorting_enabled.setter
    def sorting_enabled(self, val):
        """Sets if sorting is enabled or not"""
        self.results_table.setSortingEnabled(val)

    # # UI abstraction
    @property
    def results_table(self):
        """Returns the results table view"""
        return self.resultsTableView

    @property
    def query_input(self):
        """Returns the query input object"""
        return self.queryLineEdit

    @property
    def query_input_value(self):
        """Returns the query input value"""
        return self.query_input.text()

    @property
    def query_button(self):
        """Returns the query button object"""
        return self.queryButton

    @property
    def query_column_combobox(self):
        """Returns the QComboBox to select the columns to filter by"""
        return self.queryColumnComboBox

    @property
    def query_operator_combobox(self):
        """Returns the QComboBox to select the operation to apply"""
        return self.queryOperatorComboBox

    # UI initialization
    def setupUi(self, parent):
        # Save parent and set UI
        self.parent = parent
        if callable(getattr(super(), "setupUi", None)):
            super().setupUi(parent)
        # Setup table of results and comboboxes
        self.setup_query_column_combobox()
        self.setup_query_operator_combobox()
        self.setup_results_table()
        # Trigger updates
        self.update_results_table()
        # Attach events
        self.attach_events()

    # # UI initialization methods
    def setup_query_column_combobox(self):
        """Sets the items in the QComboBox to select the column to filter by"""
        # Column names combobox
        for column in self._columns:
            self.query_column_combobox.addItem(column)

    def setup_query_operator_combobox(self):
        """Updates the combobox to query by field with the model columns"""
        # Operators combobox
        for operator in PQSOperator.listing:
            self.query_operator_combobox.addItem(operator.name)

    def setup_results_table(self):
        """Sets the model and arranges the columns to be displayed properly"""
        # Set model
        self.results_table.setModel(self._table_model)
        # Do not allow empty last sections
        self.results_table.horizontalHeader().setStretchLastSection(True)
        # Set sorting options by default
        self.results_table.sortByColumn(self._table_model.sort_column,
                                        self._table_model.sort_order)
        # Enable sorting, (caution, will call `sort` and therefore `refresh`)
        self.sorting_enabled = self._sorting_enabled

    def update_results_table(self):
        """Updates the results table so the contents of the columns fit"""
        # Code extracted from
        # https://stackoverflow.com/questions/3433664/how-to-make-sure-columns-in-qtableview-are-resized-to-the-maximum
        visible = self.parent.isVisible()
        if not visible:
            self.parent.show()
        self.results_table.setVisible(False)
        self.results_table.resizeColumnsToContents()
        self.results_table.setVisible(True)
        if not visible:
            self.parent.hide()

    def updated_query_operator_combobox(self, operator_id):
        """When the operator combobox updates, we need to perform operations

        The operation to perform is to disable the query value input if the
        operator selected for the filter is unary
        """
        # Disable query value when using IS NULL, IS NOT NULL
        if operator_id == PQSOperatorIsNull.id \
           or operator_id == PQSOperatorIsNotNull.id:
            self.query_input.setReadOnly(True)
        else:
            self.query_input.setReadOnly(False)

    # Events
    # # Attacher
    def attach_events(self):
        """Attaches the UI interfaces"""
        # Query on return
        if isinstance(self.query_input, QLineEdit):
            self.query_input.returnPressed.connect(self.do_query)
        # Query on click
        self.query_button.clicked.connect(self.do_query)
        # Update results view
        self.table_model.layoutChanged.connect(self.update_results_table)
        # Update comboboxes
        self.query_operator_combobox.currentIndexChanged.connect(
            self.updated_query_operator_combobox)

    # Actions
    def generate_query(self):
        """Creates the SQLAlchemy query based on the form values"""
        # 0. Columns to query
        select_columns_names = self.table_model.columns
        select_columns = [getattr(self._model, name)
                          for name in select_columns_names]
        # 1. Column selected
        column_id = self.query_column_combobox.currentIndex()
        column_name = self._columns[column_id]
        column = getattr(self._model, column_name)
        # 2. Get operator
        operator_id = self.query_operator_combobox.currentIndex()
        operator_obj = PQSOperator.listing[operator_id]
        operator = getattr(column, operator_obj.operator)
        # 3. Get query value
        query_value = self.query_input_value
        if operator_id == PQSOperatorLike.id \
           or operator_id == PQSOperatorILike.id:
            if "%" not in query_value:
                query_value = "%" + query_value + "%"
        # 4. Get filter
        if operator_id == PQSOperatorIsNull.id \
           or operator_id == PQSOperatorIsNotNull.id:
            _filter = operator(None)
        elif operator_id == PQSOperatorLike.id \
             or operator_id == PQSOperatorILike.id:  # NOQA
            _filter = operator(query_value, escape="/")
        else:
            _filter = operator(query_value)
        # 5. Create query
        return self._session.query(*select_columns).filter(_filter)

    def do_query(self):
        """Generate a query with the values set in the UI and send it to DB"""
        print("yup")
        self.table_model.query = self.query
        self.table_model.refresh()
