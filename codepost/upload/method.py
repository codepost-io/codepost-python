# # =============================================================================
# # codePost v2.0 SDK
# #
# # UPLOAD METHOD SUB-MODULE ##### CODE DOES CURRENTLY NOT WORK #######
# # =============================================================================

# from __future__ import print_function # Python 2

# # Python stdlib imports
# import itertools as _itertools

# # Local imports
# from .. import errors as _errors

# from ..util import config as _config
# from ..util import logging as _logging

# from .. import instantiated as _static

# from ..util.misc import _make_f

# from . import modes as _modes

# # =============================================================================

# # Replacement f"..." compatible with Python 2 and 3
# _f = _make_f(globals=lambda: globals(), locals=lambda: locals())

# # =============================================================================

# # Global submodule constants
# _LOG_SCOPE = "{}".format(__name__)

# # Global submodule protected attributes
# _logger = _logging.get_logger(name=_LOG_SCOPE)

# # =============================================================================

# def _submission_list_is_unclaimed(submissions):
#     for submission in submissions:
#         if submission.grader is not None:
#             return False
#     return True

# def _upload_submission_filediff(submission, newest_files, mode=_modes.DEFAULT):

#     # Retrieve a submission's existing files, indexed by name
#     existing_files = {
#         file.name: file
#         for file in [
#             _static.file.retrieve(id=file_id)
#             for file_id in submission.files
#         ]
#     }

#     # Compute files that were added
#     added_file_ids = []

#     # Flag to determine whether to do the post-modification actions
#     submission_was_modified = False

#     for file in newest_files:

#         # Check if file matches existing ones (by matching name and extension)
#         if file.name in existing_files and existing_files[file.name].extension == file.extension:

#             if mode.value["updateExistingFiles"]:

#                 # FIXME: use hashing/robust method of comparing files

#                 # Ignore newlines when comparing files, to avoid a trailing newline
#                 # registering as a difference

#                 data_existing = existing_files[file.name].code.replace(
#                     "\n", "")
#                 data_new = file.code.replace("\n", "")

#                 if data_existing != data_new:

#                     submission_was_modified = True

#                     _logger.info(
#                         "Replacing contents of {} (note: all comments will be deleted)")

#                     try:
#                         _static.file.delete(id=existing_files[file.name].id)

#                         file_obj = _static.file.create(
#                             submission=submission.id,
#                             filename=file.name,
#                             content=file.code,
#                             extension=file.extension,
#                         )
#                     except:
#                         raise _errors.UploadError(
#                             message="Unexpected error while replacing a file.",
#                             # Additional fields
#                             assignment_id=submission.assignment,
#                             submission_id=submission.id,
#                             file_ids=added_file_ids,
#                         )

#                     if file_obj is not None and file_obj.id is not None:
#                         added_file_ids.append(file_obj.id)

#         else:

#             if mode.value["addFiles"]:

#                 submission_was_modified = True
#                 _logger.info("Adding file {}.".format(file.name))

#                 try:
#                     file_obj = _static.file.create(
#                         submission_id=submission.id,
#                         filename=file.name,
#                         content=file.code,
#                         extension=file.extension,
#                     )
#                 except:
#                     raise _errors.UploadError(
#                         message="Unexpected error while adding a file.",
#                         # Additional fields
#                         assignment_id=submission.assignment,
#                         submission_id=submission.id,
#                         file_ids=added_file_ids,
#                     )

#                 if file_obj != None and file_obj.id != None:
#                     added_file_ids.append(file_obj.id)

#     # Delete files in existing_files but not in newest_files, if instructed to do so
#     if mode.value["deleteUnspecifiedFiles"]:
#         newest_files_names = [ x.name for x in newest_files ]
#         for filename in existing_files.keys():
#             if filename not in newest_files_names:
#                 _logger.info(
#                         ("Deleting file {}, since it was not specified in the " +
#                          "upload and deleteUnspecifiedFiles is True.").format(filename))
#                 _static.file.delete(id=existing_files[filename].id)
#                 submission_was_modified = True

#     if not submission_was_modified:
#         _logger.info("Nothing to add or update, submission was left unchanged.")

#     return submission_was_modified

# # =============================================================================

# def upload_submission(assignment, students, files, create_files=False, mode=_modes.DEFAULT):

#     assignment_id = assignment.id
#     file_ids = [
#         _static.file.create(**file).id if create_files else file.id
#         for file in files
#     ]

#     # Retrieve all existing submissions associated with the students

#     existing_submissions = {}

#     for student in students:
#         submissions = _static.assignment.list_submissions(
#             id=assignment_id,
#             student=student,
#         )

#         for submission in submissions:
#             existing_submissions[submission.id] = submission

#     # Check to see if there is a collision

#     if len(existing_submissions) == 0:

#         # CASE 1: No existing submission => create a new submission
#         try:
#             return _static.submission.create(
#                 assignment=assignment_id,
#                 students=students,
#                 files=file_ids,
#             )
#         except _errors.UploadError as e:
#             if not mode.value["allowPartial"]:
#                 e.force_cleanup()
#             raise e
#         # END CASE 1

#     # There is at least one (maybe more) existing submissions

#     # First check the modes to determine whether to proceed.
#     if not mode.value["updateIfExists"]:
#         raise _errors.UploadError(
#             """
#             At least one submission already exists, and 'updateIfExists' is false,
#             so interrupting upload. {} {} {}
#             """.format(assignment_id, len(existing_submissions), existing_submissions))

#     # Check whether any of the existing submissions are claimed.
#     if not mode.value["updateIfClaimed"] and _submission_list_is_unclaimed(list(existing_submissions.values())):
#         raise _errors.UploadError(
#             """
#             At least one submission has already been claimed by a grader, and
#             'updateIfClaimed' is false, so interrupting upload.
#             """)

#     # Check whether students will need an update.
#     if not mode.value["resolveStudents"]: # pragma: no cover
#         # NOTE: It turns out that, as of 2019-06-18, with our current
#         # 5 different modes, this block is never executed because:
#         #     For all mode:
#         #         mode["updateIfExists"] === mode["resolveStudents"]
#         # This piece of code is left in case future modes are created.
#         if len(existing_submissions) > 1 or set(students) != set(existing_submissions[0]["students"]):
#             raise _errors.UploadError(
#                 """
#                 There are {} existing submission(s) with a different subset of
#                 students than those requested. Since 'resolveStudents' is false,
#                 interrupting upload.
#                 - Requested students: {}
#                 - Existing students (on first existing submission): {}
#                 """.format(
#                     len(existing_submissions),
#                     students,
#                     set(existing_submissions[0]["students"])
#                 ))

#     if len(existing_submissions) > 1:

#         # CASE 2: Remove the students that we need to assign to the uploaded submission
#         # from their existing submissions

#         for submission in existing_submissions:
#             submission.students = [
#                 s
#                 for s in submission.students
#                 if not s in students # students to remove
#             ]
#             submission.saveInstance()

#             if mode.value["deleteAffectedSubmissions"]:
#                 _static.submission.delete(id=submission.id)

#         try:
#             return _static.submission.create(
#                 assignment=assignment_id,
#                 students=students,
#                 files=file_ids,
#             )
#         except _errors.UploadError as e:
#             if not mode.value["allowPartial"]:
#                 e.force_cleanup()
#             raise e

#         # END CASE 2

#     # CASE 3: There is exactly one submission.
#     submission = list(existing_submissions.values())[0]
#     submission_id = submission.id

#     # Update the submission students to make sure it is what was
#     # specified (if we needed to make this change, and it was forbidden,
#     # this would already have been caught).
    
#     submission.students = students
#     submission.saveInstance()

#     # Process the change in files
#     submission_was_modified = False
#     try:
#         submission_was_modified = _upload_submission_filediff(
#             submission=submission,
#             newest_files=files,
#             mode=mode,
#         )
#     except _errors.UploadError as e:
#         if not mode.value["allowPartial"]:
#             e.force_cleanup()
#         raise e

#     # Depending on the outcome of the file changes, proceed with the
#     # finishing actions
    
#     if submission_was_modified:

#         if mode.value["removeComments"]:
#             #_remove_comments(
#             #    submission_id=submission_id,
#             #)
#             comment_ids = _itertools.chain.from_iterable([
#                 file.comments
#                 for file in submission.files
#             ])
#             for comment_id in comment_ids:
#                 _static.comment.delete(id=comment_id)

#         if mode.value["doUnclaim"]:
#             submission.grader = ""
#             submission.saveInstance()
#             #_unclaim_submission(
#             #    submission_id=submission_id,
#             #)

#     # Return updated submission dictionary (equivalent to what
#     # post_submission would return in the above exit paths)
    
#     submission = _static.submission.retrieve(id=submission_id)

#     return submission

# # =============================================================================

