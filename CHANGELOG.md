# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
Until a release is made, the progress on each commit will be detailed here

### Progress
**[01](../../commit/b81d6b02a716ddb1f331e31fea1abc944511db44): Initial, hardcoded Qt interface using SQLALchemy model**
 - Hardcoded mapper from Qt to real SQLAlchemy defined mapper

**[02](../../commit/a0b539d928daa96dac577112d83a21447110aa6b): Add abstraction: mapper abstract class, grained updater events**
 - Added QtDataMapper:
    - Maps a Qt field object (like QLineEdit) to a SQLAlchemy model field
 - Added grained updater events to QtDataMapper
    - Event-driven design in QtDataMapper for field update

**[03](../../commit/d3a1f4dde4a2e36be072594f0e357776a51c693f): Save feature: commit to database when desired:**
 - Validate all fields previous to commit to SQLAlchemy's session
 - Check if session commit succeeds or rollback automatically

**[04](../../commit/d2e1f05837a09e22b11e376f26f75105fcdc1491): Added and tested edit feature**
  - We can add the model to the session every time before commit

**[05](../../commit/ccb38db81eea02fcf338c563d712f21df79c8ce1): Edit feature completed: pass an object and UI is filled**
 - Detect add / edit mode: allow to create a UI with an object, not a class
 - The UI fills with the model values if the UI receives a filled object
 - The UI doesn't validate after filling to don't change model's values
 - Added refresh feature to get latest version from database
 - After refresh, fields are not validated to avoid changing the status
   message to "Pending changes" when object has just been refreshed.

**[06](../../commit/7605264ede316c8d6589ce34b124152304eed657): Created `PQSFieldBinder`**
 - Renamed `QtDataMapper` to `PQSFieldBinder`
 - Cleaned its code, added comments
 - Abstracted functionality
 - Added autoupdate `autoconnect` feature to connect signal and slot
   automatically

**[07](../../commit/f65bde050f032d68092da4b3b4f4c179e859f110): Created `PQSEditUI`**
 - Allows to design a UI in QtDesigner to set as edit UI
 - Allows to design a separate UI in QtDesigner for the model fields:
    - Implements pre-defined `PQSFieldBinder` for following QWidgets:
      `QLineEdit`, `QDateEdit`
    - Searches binders in form, creates default binders by name if not found:
      `birthdateDateEdit` -> `QDateEditPQSFieldBinder`
 - Added disabled feature for fields that must not be edited (`id`)
 - Changed behaviour of `PQSEditUI.commit`: reloads from model after save
   (because some fields may be autocalculated like `id`)
 - Added autosave feature in PQSFieldBinder
 - Added and tested `QDateEdit` default `PQSFieldBinder`
 - Added automatic session management from `sessionmaker` factory
 - Renamed `PQSFieldBinder.mark_as_notvalidated` to 
   `PQSFieldBinder.mark_as_not_validated`
 - Changed behaviour of `PQSFieldBinder.update_to_gui`: doesn't call 
   `PQSFieldBinder.mark_as_not_validated`
 - Updated behaviour of `PQSEditUI.update_to_gui`: calls 
   `PQSFieldBinder.mark_as_not_validated` by default but allows to avoid call 
   if field is already validated
 - Improved `PQSFieldBinder.bind_form` by using `PQSEditUI.update_to_gui`
 - Added disabled message if field is generated automatically

**[08](../../commits/5630ed78346d42b66e74ee47ccb9ee0880d63ef5): Abstracted `PQSEditUi`**
 - Removed `QMessageBox`, replaced by custom exceptions
 - Added exceptions for different kinds of possible user messages
 - Added and tested delete feature and button
 - Clean code and commented methods
 - Split `update_status` to be event-driven
 - Added events to respond for action buttons like `_on_save`
 - Split __init__ in `_set_model` and `_set_session`
 - Added checks before setting model and setting session
 - Added several properties so all attributes are accesible
 - Added properties to retrieve action buttons so they can be renamed
 - Added `validate_binders` method to check if a list of binders is valid
 - Split `bind_form` to create `attach_events` method
 - Fixed `update_to_gui` failing to validate
 - Adapted `__main__` code to suit the new style

**[09](../../commits/master): Split into package `pqs`**
 - Split `bindings.py` into `pqs` package
 - Commented each `pqs` package's module
 - Created `test` package, updated code to get it from `pqs` package
 - Adapted `.atom-build.yaml` settings to match new code distribution
