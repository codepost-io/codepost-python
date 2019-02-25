#!/usr/bin/env python3
##########################################################################
# codePost submission utils
#
# DATE:    2019-02-12
# AUTHOR:  codePost (team@codepost.io)
#
##########################################################################

import os
import requests
import sys
UF_CAUTIOUS = 0
UF_EXTEND = 1
UF_DIFFSCAN = 2
UF_OVERWRITE = 3
UF_PREGRADE = 4

UPLOAD_FLAGS = [

    # Mode 0: Cautious
    # Description: If a submission already exists for this
    # (student, assignment) pair (including partners),
    # then abort the upload.
    # If no such submission exists, create it.
    UF_CAUTIOUS,

    # Mode 1: Extend
    # Description: If a submission already exists for this
    # (student, assignment) pair (including partners),
    # then check to see if any files (key = name) in the upload request are not
    # linked to the existing submission.
    # If so, add these files to the submission.
    # Does not unclaim submission upon successful extension.
    UF_EXTEND,

    # Mode 2: Diff Scan
    # Description: If a submission already exists for this
    # (student, assignment) pair (including partners),
    # compare the contents of uploaded files with their
    # equivalent in the request body (key = (name, extension), value = code).
    # If any files do not match, overwrite the uploaded files with equivalents.
    # If no matching file exists in the submission, add it (same behavior as Extend). If
    # any existing files are overwritten, clear comments
    # on these files.
    # Does not unclaim submission upon successful extension.
    UF_DIFFSCAN,

    # Mode 3: Hard Overwrite
    # Description: If a submission already exists for this
    # (student, assignment) pair (including partners),
    # overwrite it with the contents of the request. Keep the existing submission
    # linked to any partners not included in the reuqest.
    # Delete any existing comments, unclaim submission,
    # and set grader field to None.
    UF_OVERWRITE,

    # Mode 4: Pregrade Mode
    # Description: If a submission has not been claimed, overwrite
    UF_PREGRADE
]

BASE_URL = 'https://api.codepost.io'

##########################################################################


class color:
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


_TERM_INFO = (color.END + "[" + color.BOLD +
              "INFO" +
              color.END + "]" + color.END)


try:
    import click
except ImportError:
    print(_TERM_ERROR + " This tool requires the 'click' python package.", file=sys.stderr)
    print("Try installing the package locally:", file=sys.stderr)
    print("    pip install --user click", file=sys.stderr)
    sys.exit(99)


def _print_info(msg):
    click.echo(message=_TERM_INFO + " " + msg, err=True)

########################################################################################
# Primary methods (which can be called directly in a client script)
########################################################################################


def upload_single_submission(api_key,
                             course_name,
                             course_period,
                             assignment_name,
                             students,
                             files,
                             mode=UF_CAUTIOUS):

    cpAssignment = get_assignment_info(
        api_key, course_name, course_period, assignment_name)
    if cpAssignment is not None:
        return upload_submission(api_key, cpAssignment, students, files, mode)

    return None


def upload_submission(api_key, assignment, students, files, mode=UF_CAUTIOUS):
    """
    Arguments:
    - api_key
    - assignment = codePost assignment object
    - students = list of emails
    - files = list of partial file payloads (excludes submission identifier).
      {
        code: <code here as string>,
        name: <string>,
        extension: <string>
      }
    - mode = element of UPLOAD_FLAGS

    """

    # See if any students already have submissions for this assignment. In other words, look for
    # (submission, student) collisions.
    collisions = []
    auth_headers = {"Authorization": "Token %s" % (api_key)}
    for student in students:
        r = requests.get('%s/assignments/%d/submissions?student=%s' %
                         (BASE_URL, assignment['id'], student), headers=auth_headers)
        if r.status_code != 200:
            msg = "An error occurred when checking for pre-existing submissions to find this assignment. {}"
            raise RuntimeError(msg.format(r.content))

        # This list of length 0 or 1 corresponding to student's submission for
        # this assignment
        submissions = r.json()
        if len(submissions) > 0:
            firstSubmission = submissions[0]
            # If multiple students, we'll get multiple submissions, so need to
            # check for id Uniqueness before appending
            if (len(list(filter(lambda x: x['id'] == firstSubmission['id'], collisions))) == 0):
                collisions.append(firstSubmission)

    # CASE 1: Collisions exist, and students group does not map to a submission,
    # either because students correspond to multiple submissions, or not all partners
    # are present.
    if len(collisions) > 1 or (len(collisions) == 1 and set(students) != set(collisions[0]['students'])):

        # Abort
        if mode == UF_CAUTIOUS:
            msg = "Multiple collisions exist for this student group. We are in cautious mode, so aborting."
            raise RuntimeError(msg)

        # Abort
        elif mode == UF_EXTEND:
            msg = "Multiple collisions exist for this student group. We are in extend mode, so aborting."
            raise RuntimeError(msg)

        # Abort
        elif mode == UF_DIFFSCAN:
            msg = "Multiple collisions exist for this student group. We are in diffscan mode, so aborting."
            raise RuntimeError(msg)

        # Delete all collisions owned by students in our list.
        # If there exist collisions that contain students in our list and other students, remove our
        # students from these submissions to clear the way to post a new one.
        # Then post, the new submission.
        elif mode == UF_OVERWRITE:
            for collision in collisions:
                remove_students_from_submission(api_key, collision, students)

            # We are ready to create the submission
            return post_submission(api_key, assignment['id'], students, files)

        elif mode == UF_PREGRADE:
            # Check to see if a grader is assigned to any submission
            # Note we need to do this check before making any modifications
            if not submission_list_is_unclaimed(collisions):
                msg = "Multiple collisions exist for this student group, and at least one has been assigned to a grader. We are in pregrade mode, so aborting."
                raise RuntimeError(msg)

            # We can proceed with overwrite
            for collision in collisions:
                remove_students_from_submission(api_key, collision, students)

            # We are ready to create the submission
            return post_submission(api_key, assignment['id'], students, files)

    # Case 2: Collision exists, but there is only one, and its student list
    # corresponds to the partners list we are trying to use. In other words,
    # this submission we are uploading already exists.
    elif len(collisions) == 1 and set(students) == set(collisions[0]['students']):
        if mode == UF_CAUTIOUS:
            # abort
            msg = "This submission already exists. We are in cautious mode, so aborting."
            raise RuntimeError(msg)

        elif mode == UF_EXTEND:
            # Scan submission to see if we can extend it with any files
            return diffscan_submission(api_key, collisions[0], files, EXTEND_ONLY=True)

        elif mode == UF_DIFFSCAN:
            # Scan submission for diffs and extends
            return diffscan_submission(api_key, collisions[0], files, EXTEND_ONLY=False)

        elif mode == UF_OVERWRITE:
            # Overwrite
            delete_submission(api_key, collisions[0]['id'])
            return post_submission(api_key, assignment['id'], students, files)

        elif mode == UF_PREGRADE:
            # Check to see if a grader is assigned to any submission
            # If yes => abort
            if not submission_list_is_unclaimed(collisions):
                msg = "This submission has already been assigned to a grader. We are in pregrade mode, so aborting."
                raise RuntimeError(msg)

            # If no => delete and overwrite
            delete_submission(api_key, collisions[0]['id'])
            return post_submission(api_key, assignment['id'], students, files)

    # Case 3: No collisions
    else:
        return post_submission(api_key, assignment['id'], students, files)


def get_assignment_info(api_key, course_name, course_term, assignment_name):
    """
    Tries to find the assignment corresponding to (course name, course period, assignment name).
    If this assignment exists and the API key in use has access to it, return that assignment.
    Otherwise, return None.
    """

    auth_headers = {"Authorization": "Token %s" % (api_key)}

    # Get all of the courses to which this API key has access
    r = requests.get(BASE_URL + '/users/me/', headers=auth_headers)
    if r.status_code != 200:
        msg = "An error occurred when attempting to access this API Key's course list. {}"
        raise RuntimeError(msg.format(r.content))

    # List of course objects to which API key has access
    courses = r.json()['courseadminCourses']
    targetName = course_name
    targetTerm = course_term

    thisCourse = None
    for course in courses:
        if course['name'] == targetName and course['period'] == targetTerm:
            thisCourse = course
            break

    if not thisCourse:
        msg = """Either no course with the specified course ({}) and period ({}) exists,
    or this API key does not have access to it. """
        msg.format(msg.format(targetName, targetTerm))
        return None

    assignments = thisCourse['assignments']  # list of IDs
    targetAssignment = None
    for aid in assignments:
        r = requests.get(BASE_URL + '/assignments/%d/' %
                         (aid), headers=auth_headers)
        if r.status_code != 200:
            msg = "An error occurred when trying to find this assignment. {}"
            raise RuntimeError(msg.format(r.content))

        tempAssignment = r.json()

        # Is this the one we're looking for?
        targetName = assignment_name
        if tempAssignment['name'] == targetName:
            targetAssignment = tempAssignment
            break

    if not targetAssignment:
        msg = "No assignment with name {} was found in {} | {}."
        raise RuntimeError(msg.format(assignment_name, thisCourse[
            'name'], thisCourse['period']))

    return targetAssignment

########################################################################################
# Helper methods
########################################################################################


def diffscan_submission(api_key, submission, newFiles, EXTEND_ONLY=True):
    # Retrieve all submission's files
    existingFiles = {}

    weDidSomething = False
    auth_headers = {"Authorization": "Token %s" % (api_key)}
    for fileID in submission['files']:
        r = requests.get('%s/files/%d/' %
                         (BASE_URL, fileID), headers=auth_headers)
        if r.status_code != 200:
            msg = "An error occurred when retrieving existing submission's file. {}"
            raise RuntimeError(msg.format(r.content))

        existingFile = r.json()
        existingFiles[existingFile['name']] = existingFile

    for file in newFiles:

        # Check if file matches any (by name AND extension)
        if file['name'] in existingFiles and existingFiles[file['name']]['extension'] == file['extension']:

            # If we are diffscanning in addition to extending, compare code
            if not EXTEND_ONLY:

                # Ingore newlines when comparing files, to avoid trailing newLine registering a diff
                if file['code'].replace('\n', "") != existingFiles[file['name']]['code'].replace('\n', ""):
                    # If different => delete file (which will delete comments)
                    # and create a new one
                    weDidSomething = True
                    msg = "Replacing contents of %s (note: all comments will be deleted)" % (
                        file['name'])
                    _print_info(msg)
                    delete_file(api_key, existingFiles[
                                file['name']]['id'])
                    post_file(api_key, submission['id'], file[
                              'name'], file['code'], file['extension'])

        # If not => extend submission by adding file
        else:
            weDidSomething = True
            msg = "Adding file %s" % (file['name'])
            _print_info(msg)
            post_file(api_key, submission['id'], file[
                      'name'], file['code'], file['extension'])

    if not weDidSomething:
        msg = "Nothing to add or update, so the submission was left unchanged."
        _print_info(msg)

    return


def remove_students_from_submission(api_key, submission, students_to_remove):
    # Students to Remove should be a list of strings
    assert isinstance(students_to_remove, list)

    # NOTE: The check below was spurious, and so has been removed.
    # for student in students_to_remove:
    #     if student not in submission['students']:
    #         msg = 'Student %s is not in the submission to be removed' % (
    #             student)
    #         raise RuntimeError(msg)

    newStudentList = list(filter(
        lambda student: student not in students_to_remove, submission['students']))
    if len(newStudentList) == 0:
        # no students remain, so delete submission
        # NOTE: perhaps we should return False here and print a warning telling
        # script user to use delete_submission
        return delete_submission(api_key, submission['id'])
    else:
        payload = {
            'students': newStudentList
        }

        auth_headers = {"Authorization": "Token %s" % (api_key)}
        r = requests.patch('%s/submissions/%d/' % (BASE_URL,
                                                   submission['id']), data=payload, headers=auth_headers)
        if r.status_code != 200:
            msg = "An error occurred when removing students from a submission. {}"
            raise RuntimeError(msg)

    return True


def post_submission(api_key, assignmentID, students, files):

    # Create submission payload, which is just a bucket for files
    payload = {
        'assignment': assignmentID,
        'students': students,
    }

    auth_headers = {"Authorization": "Token %s" % (api_key)}
    r = requests.post('%s/submissions/' % (BASE_URL),
                      headers=auth_headers, data=payload)
    if r.status_code != 201:
        msg = "An error occurred when creating a submission. {}"
        raise RuntimeError(msg.format(r.content))

    submission = r.json()

    for file in files:
        post_file(api_key, submission['id'], file[
                  'name'], file['code'], file['extension'])

    return


def post_file(api_key, submissionID, name, code, extension):

    # Create file payload
    payload = {
        'submission': submissionID,
        'name': name,
        'code': code,
        'extension': extension
    }

    auth_headers = {"Authorization": "Token %s" % (api_key)}
    r = requests.post('%s/files/' % (BASE_URL),
                      headers=auth_headers, data=payload)
    if r.status_code != 201:
        msg = "An error occurred when creating a file. {}"
        raise RuntimeError(msg.format(r.content))

    return r.json()


def delete_file(api_key, fileID):
    auth_headers = {"Authorization": "Token %s" % (api_key)}
    r = requests.delete('%s/files/%d/' %
                        (BASE_URL, fileID), headers=auth_headers)
    if r.status_code != 204:
        msg = "An error occurred when deleting a submission. {}"
        raise RuntimeError(msg.format(r.content))

    return True


def delete_submission(api_key, submissionID):
    auth_headers = {"Authorization": "Token %s" % (api_key)}
    r = requests.delete('%s/submissions/%d/' %
                        (BASE_URL, submissionID), headers=auth_headers)
    if r.status_code != 204:
        msg = "An error occurred when deleting a submission. {}"
        raise RuntimeError(msg.format(r.content))

    return True


def submission_list_is_unclaimed(submissions):
    for submission in submissions:
        if submission['grader'] is not None:
            return False
    return True
