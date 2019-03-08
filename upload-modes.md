In this document we are trying to redefine the modes that are built into the codePost Python library.

# New mode

Proposal of a mode definition according to the following criteria:

- updateExisting:
- updateClaimed:
- doUnclaim:
- addFiles:
- changeFiles:
- changeStudents:
- removeComments:

# Old modes

## UF_CAUTIOUS, Mode 0: Cautious

- If a submission already exists for this (student, assignment) pair (including partners), then abort the upload.
- If no such submission exists, create it.

* updateExisting: false
* updateClaimed: false
* doUnclaim: true
* addFiles: false
* changeFiles: false
* changeStudents: false
* removeComments: false

## UF_EXTEND, Mode 1: Extend

- If a submission already exists for this (student, assignment) pair (including partners), then check to see if any files (key = name) in the upload request are not linked to the existing submission.
- If so, add these files to the submission.
- Does not unclaim submission upon successful extension.

* updateExisting: true
* updateClaimed: false
* doUnclaim: false
* addFiles: true
* changeFiles: false
* changeStudents: false
* removeComments: false

## UF_DIFFSCAN, Mode 2: Diff Scan

- If a submission already exists for this (student, assignment) pair (including partners), compare the contents of uploaded files with their equivalent in the request body (key = (name, extension), value = code).
- If any files do not match, overwrite the uploaded files with equivalents.
- If no matching file exists in the submission, add it (same behavior as Extend). If any existing files are overwritten, clear comments on these files.
- Does not unclaim submission upon successful extension.

* updateExisting: true
* updateClaimed: false
* doUnclaim: false
* addFiles: true
* changeFiles: true
* changeStudents: false
* removeComments: true

## UF_OVERWRITE, Mode 3: Hard Overwrite

- If a submission already exists for this (student, assignment) pair (including partners), overwrite it with the contents of the request. Keep the existing submission linked to any partners not included in the reuqest.

- Delete any existing comments, unclaim submission, and set grader field to None.

* updateExisting: true
* updateClaimed: true
* doUnclaim: true
* addFiles: true
* changeFiles: true
* changeStudents: false
* removeComments: true

## UF_PREGRADE, Mode 4: Pregrade Mode

- If a submission has not been claimed, overwrite

* updateExisting: true
* updateClaimed: false
* doUnclaim: false
* addFiles: true
* changeFiles: true
* changeStudents: true
* removeComments: true
