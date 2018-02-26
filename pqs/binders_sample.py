"""Defines sample binders for common QtWidgets used as user inputs

Classes:
    QLineEditBinder: sample binder for a `QLineEdit` user input widget
    QDateEditBinder: sample binder for a `QDateEdit` user input widget
"""
# Libraries
# # Internal
from .binder import PQSFieldBinder


# Classes
class QLineEditBinder(PQSFieldBinder):
    """Sample binder for a `QLineEdit` user input"""
    DISABLED_MESSAGE = "<<<Auto>>>"
    """
        str: message to display if field is disabled (autocalculated)
    """

    @property
    def gui_value(self):
        """Returns the `QLineEdit` text

        Returns:
            str: string in the user input field or `None` if empty string
        """
        # Retrieve real input value
        get_value = self._gui_field.text()
        # See if empty
        if len(get_value):
            # See if it matches disabled message
            if get_value == self.DISABLED_MESSAGE:
                return None
            else:
                return get_value
        else:
            # Empty, return `None`
            None

    @gui_value.setter
    def gui_value(self, new_value):
        """Sets the `QLineEdit` text

        Args:
            str: string to set in the input field, if `None` will set an empty
                 string
        """
        # Define value to set
        set_value = new_value
        # Check if value to set is `None`
        if new_value is None:
            # If disabled, show disabled message
            if self._disabled:
                set_value = self.DISABLED_MESSAGE
            # If not disabled, show empty string
            else:
                set_value = ""
        # Convert to string if not a string
        elif not isinstance(new_value, str):
            set_value = str(set_value)
        # Set value to GUI
        self._gui_field.setText(set_value)

    @property
    def signal_autoupdate(self):
        """Returns the signal to detect changes so autoupdate is triggered

        In this case, when the field is changed either programatically or
        edited by the user manually
        """
        return self._gui_field.textChanged

    @property
    def signal_save(self):
        """Returns the signal to detect when user wants to save changes

        In this case, when user press `Return` key
        """
        return self._gui_field.returnPressed

    def is_edit_disabled(self):
        """Returns whether the field is disabled"""
        return self._gui_field.isReadOnly()

    def override_disable_edit(self):
        """Sets the field as disabled so user can't edit it"""
        self._gui_field.setReadOnly(True)

    def override_enable_edit(self):
        """Sets the field as enabled so user can edit it"""
        self._gui_field.setReadOnly(False)


class QDateEditBinder(PQSFieldBinder):
    """Sample binder of a `QDateEdit` user input field"""
    @property
    def gui_value(self):
        """Returns the date value set by the user in the field

        Converts to a Python compatible built-in datetime.date object

        Returns:
            datetime.date: date object with the date set in the GUI
        """
        return self._gui_field.date().toPyDate()

    @gui_value.setter
    def gui_value(self, date):
        """Sets the date value in the user field

        Args:
            date (datetime.date): date object to set in the user input
        """
        if date is not None:
            self._gui_field.setDate(date)

    @property
    def signal_autoupdate(self):
        """Returns signal to detect changes so `autoupdate` is triggered

        In this case, when date changes
        """
        return self._gui_field.dateChanged

    def is_edit_disabled(self):
        """Returns whether the field is disabled"""
        return self._gui_field.isReadOnly()

    def override_disable_edit(self):
        """Sets the field as disabled so user can't edit it"""
        self._gui_field.setReadOnly(True)

    def override_enable_edit(self):
        """Sets the field as disabled so user can edit it"""
        self._gui_field.setReadOnly(False)
