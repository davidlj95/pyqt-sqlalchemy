"""Test the framework with a sample model"""
# Libraries
# # Built-in
import sys
import datetime
# # Internal
from .design.user_form import Ui_UserForm
from .design.edit_form import Ui_EditForm
from .design.connect_form import Ui_ConnectForm
from .design.query_form import Ui_QueryForm
from pqs import PQSEditUI, bind_engine, Base, SessionFactory, \
                PQSConnectDefaultUI, is_engine_binded, get_engine, PQSQueryUI
# # External
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from sqlalchemy import Column, String, Integer, create_engine, Date
from sqlalchemy.orm import validates

# Constants
TEST_CASES = ["add", "edit-transient", "edit-pending", "edit-persistent",
              "edit-persistent-wrong", "connect", "query"]
AFTER_CONNECT_TEST = None
AFTER_EDIT_TEST = None
MEM = []


# Test model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(50), nullable=False)
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


# Connect UI
class ConnectUI(PQSConnectDefaultUI, Ui_ConnectForm):
    @property
    def connector_input(self):
        return self.connectorComboBox

    @property
    def connector_input_value(self):
        return self.connector_input.currentText()

    @property
    def port_input(self):
        return self.portSpinBox

    @property
    def port_input_value(self):
        return str(self.port_input.value())

    def on_create(self, uri):
        print("Tried to create engine from URI: %s" % uri)

    def on_create_success(self, uri, eng):
        QMessageBox.information(None, "Connected succesfully",
                                "URI is %s\nEngine is %s" % (uri, eng))
        print("Created succesfully an engine")
        if callable(AFTER_CONNECT_TEST):
            AFTER_CONNECT_TEST()

    def on_create_failed(self, uri, exc):
        import traceback
        msg = QMessageBox()
        msg.setText("Unable to connect")
        msg.setInformativeText("URI is: %s\nError is: %s" % (uri, str(exc)))
        msg.setDetailedText(traceback.format_exc())
        msg.exec()
        print("Failed to create an engine")
        traceback.print_exc()


def ensure_engine_exists():
    """Ensures an engine exists or creates a temp one"""
    # Check if engine is present
    if not is_engine_binded():
        print("Binding new engine")
        bind_engine(create_engine("sqlite:///:memory:", echo=True))


def test_connect(widget):
    """Tests the connect mode"""
    ui = ConnectUI(opts={"echo": True})
    ui.setupUi(widget)
    ui.connector_input.setCurrentIndex(3)
    ui.host_input.setText("127.0.0.1")
    ui.port_input.setValue(3307)
    ui.username_input.setText("ibcrg")
    ui.password_input.setText("ibcrg")
    ui.database_input.setText("ibcrg")
    ui.connect_button.setFocus(Qt.OtherFocusReason)
    # continue with the engine added
    if len(sys.argv) > 2:
        if sys.argv[2] in TEST_CASES and sys.argv[2] != "connect":
            print("Next test cases will continue with the specified engine")
            test_case = sys.argv[2]
            global AFTER_CONNECT_TEST

            def AFTER_CONNECT_TEST():
                global MEM
                widget = QWidget()
                res = test_edit(test_case, widget) if test_case != "query" \
                    else test_query(widget)
                widget.show()
                MEM += [widget, res]
        else:
            print("Invalid next test case")
            print("Choose next test case from %s" % str(TEST_CASES))
            print("(Except \"connect\")")
    else:
        print("No more test cases will be performed")
    return ui


def test_edit(test_case, widget):
    """Tests the EditUI with the passed test case

    Valid test_case is supposed or doesn't perform any test
    """
    ensure_engine_exists()
    # Create schem
    Base.metadata.create_all(get_engine())
    # Create editing UI
    edit_ui = type("CustomEditUI", (Ui_EditForm, PQSEditUI), {})
    ui, s, u = None, None, None
    # Switch test
    print(test_case)
    if test_case == "add":
        ui = edit_ui(User)
    elif test_case == "edit-transient":
        ui = edit_ui(User(email="transient@users.org", number=1))
    else:
        s = SessionFactory()
        if test_case == "edit-pending":
            u = User(email="pending@users.org", number=2)
            s.add(u)
            ui = edit_ui(u, s)
        elif test_case == "edit-persistent":
            u = User(email="persistent@users.org", number=3,
                     birthdate=datetime.date(1995, 9, 21))
            s.add(u)
            s.commit()
            ui = edit_ui(u, s)
        elif test_case == "edit-persistent-wrong":
            s.execute("INSERT INTO users (email, number, birthdate) VALUES (" +
                      "\"persistent-wrongusers.org\", 4, \"2099-12-12\")")
            s.commit()
            u = s.query(User).filter(
                User.email == "persistent-wrongusers.org").first()
            ui = edit_ui(u, s)
    # Create UI
    ui.setup_and_bind(widget, Ui_UserForm)
    return ui, s, u


def test_query(widget):
    """Tests the querying UI"""
    ensure_engine_exists()
    # Create schem
    Base.metadata.create_all(get_engine())
    # Query Ui
    query_ui = type("CustomQueryUI", (PQSQueryUI, Ui_QueryForm), {})
    ui = query_ui(User)
    ui.setupUi(widget)
    return ui


# run
if __name__ == "__main__":
    # prepare scenario
    test_case = TEST_CASES[0]
    # # args
    if len(sys.argv) > 1:
        if sys.argv[1] in TEST_CASES:
            test_case = sys.argv[1]
        else:
            print("Unknown test")
            print("Please choose one from %s" % str(TEST_CASES))
            sys.exit(1)
    else:
        print("Using default test case: %s" % test_case)
    # init application
    app = QApplication(sys.argv)
    widget = QWidget()
    # test
    print("Selected test: %s" % test_case)
    if test_case == "connect":
        ui = test_connect(widget)
    elif test_case == "query":
        ui = test_query(widget)
    else:
        ui = test_edit(test_case, widget)
    # Run and show
    widget.show()
    if test_case == "connect":
        ui.connect_button.setFocus(Qt.OtherFocusReason)
    sys.exit(app.exec_())
