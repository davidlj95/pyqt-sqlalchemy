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

**[06](../../commit/master): Created PQSFieldBinder**
 - Renamed `QtDataMapper` to `PQSFieldBinder`
 - Cleaned its code, added comments
 - Abstracted functionality
 - Added autoupdate `autoconnect` feature to connect signal and slot
   automatically
