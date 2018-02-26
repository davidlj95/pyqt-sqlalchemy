"""Test the framework with a sample model"""
# Libraries
# # Built-in
import sys
import datetime
# # Internal
from .design.user_form import Ui_UserForm
from .design.edit_form import Ui_EditUI
from pqs import PQSEditUI, bind_engine, Base, SessionFactory
# # External
from PyQt5.QtWidgets import QApplication, QWidget
from sqlalchemy import Column, String, Integer, create_engine, Date
from sqlalchemy.orm import validates

# Constants
MODES = ["add", "edit-transient", "edit-pending", "edit-persistent",
         "edit-persistent-wrong"]


# Test model
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
    bind_engine(engine)
    Base.metadata.create_all(engine)
    # # Qt
    app = QApplication(sys.argv)
    widget = QWidget()
    print("ui mode: %s" % mode)
    edit_ui = type("CustomEditUI", (Ui_EditUI, PQSEditUI), {})
    if mode == "add":
        ui = edit_ui(User)
    elif mode == "edit-transient":
        ui = edit_ui(User(email="transient@users.org", number=1))
    elif mode == "edit-pending":
        u = User(email="pending@users.org", number=2)
        s = SessionFactory()
        s.add(u)
        ui = edit_ui(u, s)
    elif mode == "edit-persistent":
        u = User(email="persistent@users.org", number=3,
                 birthdate=datetime.date(1995, 9, 21))
        s = SessionFactory()
        s.add(u)
        s.commit()
        ui = edit_ui(u, s)
    elif mode == "edit-persistent-wrong":
        s = SessionFactory()
        s.execute("INSERT INTO users (email, number, birthdate) VALUES (" +
                  "\"persistent-wrongusers.org\", 4, \"2099-12-12\")")
        s.commit()
        u = s.query(User).first()
        ui = edit_ui(u, s)
    ui.setup_and_bind(widget, Ui_UserForm)
    widget.show()
    # run and show
    sys.exit(app.exec_())
