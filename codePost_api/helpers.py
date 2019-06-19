#!/usr/bin/env python3
##########################################################################
# codePost submission utils
#
# DATE:    2019-02-12
# AUTHOR:  codePost (team@codepost.io)
#
##########################################################################

from __future__ import print_function # Python 2

#####################
# Python dependencies
#
import sys as _sys

#######################
# External dependencies
#
import requests as _requests

####################
# Local dependencies
#
from . import util as _util

from .util import DocEnum as _DocEnum
from .util import urlencode as _urlencode
from .util import urlquote as _urlquote

from .util import BASE_URL

from . import errors as _errors

##########################################################################


_logger = _util.get_logger(__name__)

###########################################################################################
# Helper functions
###########################################################################################


def get_available_courses(api_key, course_name=None, course_period=None):
    """
    Returns a list of the available courses/terms to which the user, associated with
    the provided API key, has administrative access to. Optionally, restrict the
    results to a specific course and/or period.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    result = None

    try:
        r = _requests.get(
            "{}/courses/".format(BASE_URL),
            headers=auth_headers
        )

        if r.status_code != 200:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        result = r.json()

    except Exception as exc:

        raise RuntimeError(
            """
            get_available_courses: Unexpected exception while retrieving
            the list of available courses/terms; this could be related
            to the API key({:.5}...) being either unavailable, invalid,
            or stale:
               {}
            """.format(api_key, exc)
        )

    # Optionally filter according to the `course_name` parameter
    if course_name != None:
        result = filter(lambda course: course.get(
            "name") == course_name, result)

    # Optionally filter according to the `course_period` parameter
    if course_period != None:
        result = filter(lambda course: course.get(
            "period") == course_period, result)

    return list(result)


def get_course_roster_by_id(api_key, course_id):
    """
    Returns the course roster, given the course's ID. The course ID
    can be obtained from `get_available_courses`; alternatively you
    can directly obtain the course roster using the course name and
    period if you know it with `get_course_roster_by_name`.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    try:
        r = _requests.get(
            "{}/courses/{:d}/roster/".format(BASE_URL, course_id),
            headers=auth_headers
        )

        if r.status_code != 200:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return r.json()

    except Exception as exc:
        raise RuntimeError(
            """
            get_course_roster_by_id: Unexpected exception while retrieving the
            course roster from the provided course id({: d}):
               {}
            """.format(course_id, exc)
        )

def get_course_roster_by_name(api_key, course_name, course_period):
    """
    Returns the course information and roster for a course, given its
    name and period. Will throw an exception if no such course is
    available, or if either of the arguments are left blank and more
    than one course is matched.
    """

    courses = get_available_courses(
        api_key=api_key,
        course_name=course_name,
        course_period=course_period)

    if len(courses) == 0:
        raise RuntimeError(
            ("get_course_roster_by_name: No course '{course_name}_{course_name}' "
             "is available, or codePost API key '{api_key:.5}...' is invalid or "
             "does not have access to it.").format(
                 api_key=api_key,
                 course_name=course_name,
                 course_period=course_period,
            )
        )
    elif len(courses) > 1:
        raise RuntimeError(
            ("get_course_roster_by_name: Several courses match the filter "
             " '{course_name}_{course_name}' your filtering criteria must be "
             "narrower as only one course can be queried for the time "
             "being.").format(
                 course_name=course_name,
                 course_period=course_period,
            )
        )

    course_info = courses[0]

    course_roster = get_course_roster_by_id(
        api_key=api_key,
        course_id=course_info["id"]
    )

    # Combine course info and roster for convenience
    # (hey, we think deeply about our users comfort and convenience!!!)

    course_info.update(course_roster)

    return course_info

def get_assignment_info_by_id(api_key, assignment_id):
    """
    Returns the assignment information dictionary, given the assignment's ID.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    try:
        r = _requests.get(
            "{}/assignments/{:d}/".format(BASE_URL, assignment_id),
            headers=auth_headers
        )

        if r.status_code != 200:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return r.json()

    except Exception as exc:
        raise RuntimeError(
            """
            get_assignment_info_by_id: Unexpected exception while retrieving the
            assignment info from the provided id({: d}):
               {}
            """.format(assignment_id, exc)
        )

def get_assignment_info_by_name(api_key, course_name, course_period, assignment_name):
    """
    Returns the assignment information dictionary, given a(course name, course period,
    assignment name) tuple. This contains, in particular, the ID of the assignment that
    is considered.
    """
    _auth_headers = {"Authorization": "Token {}".format(api_key)}

    # Retrieve all available courses
    courses = get_available_courses(
        api_key=api_key,
        course_name=course_name,
        course_period=course_period
    )

    # Check there is exactly one course
    if len(courses) == 0:
        raise RuntimeError(
            """
            get_assignment_info_by_name: Either no course with the
            specified course({}) and period({}) exists, or the provided
            API key({:.5}...) does not have access to it.
            """.format(course_name, course_period, api_key)
        )

    elif len(courses) > 1:
        raise RuntimeError(
            """
            get_assignment_info_by_name: Request the provided course
            name({}) and period({}) resulted in more than one result({}).
            """.format(course_name, course_period, len(courses))
        )

    # Only one course selected
    selected_course = courses[0]

    # Retrieve the list of the course' assignments IDs
    assignments = selected_course.get("assignments", list())

    # Search through available assignments for matching name
    selected_assignment = None

    try:
        for aid in assignments:

            ret = get_assignment_info_by_id(api_key=api_key, assignment_id=aid)

            if ret.get("name") == assignment_name:
                selected_assignment = ret
                break

    except Exception as exc:

        raise RuntimeError(
            """
            get_assignment_info_by_name: Unexpected exception while listing the
            available assignments and searching for '{}' in course '{}', period
            '{}':
               {}
            """.format(assignment_name, course_name, course_period, exc)
        )

    return selected_assignment


def get_assignment_submissions(api_key, assignment_id, student=None, grader=None):
    """
    Returns the list of submissions of an assignment, provided an assignment ID
    and, optionally, a student.
    """

    auth_headers = {"Authorization": "Token {}".format(api_key)}

    result = None

    try:
        request_url = "{}/assignments/{}/submissions".format(
            BASE_URL,
            assignment_id
        )

        url_query = {}

        if student != None:
            # Filter according to a specific student (will be URL-quoted later)
            url_query["student"] = student

        if grader != None:
            # Filter according to a specific grader (will be URL-quoted later)
            url_query["grader"] = grader

        if len(url_query) > 0:
            request_url += "?{}".format(_urlencode(url_query))

        r = _requests.get(request_url, headers=auth_headers)

        if r.status_code != 200:
            raise RuntimeError(
                "HTTP request returned {}: {}".format(
                    r.status_code,
                    r.content
                ))

        result = r.json()

    except Exception as exc:

        # Adapt error message, according to whether student was specified
        student_msg = ""
        if student != None:
            student_msg = " associated with student '{}'".format(
                _urlquote(student))

        raise RuntimeError(
            """
            get_assignment_submissions: Unexpected exception while trying to
            retrieve submissions from assignment '{}'{};
               {}
            """.format(
                assignment_id,
                student_msg,
                exc
            ))

    return result

def get_submission_by_id(api_key, submission_id):
    """
    Returns the submission information dictionary, given the submission's ID.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    try:
        r = _requests.get(
            "{}/submissions/{:d}/".format(BASE_URL, submission_id),
            headers=auth_headers
        )

        if r.status_code != 200:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return r.json()

    except Exception as exc:
        raise RuntimeError(
            """
            get_submission_by_id: Unexpected exception while retrieving the
            submission from the provided id({: d}):
               {}
            """.format(submission_id, exc)
        )

def get_file(api_key, file_id):
    """
    Returns the file given its file ID; the file IDs are provided within a
    submissions information.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    try:
        r = _requests.get(
            "{}/files/{:d}/".format(BASE_URL, file_id),
            headers=auth_headers
        )

        if r.status_code != 200:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return r.json()

    except Exception as exc:
        raise RuntimeError(
            """
            get_file: Unexpected exception while retrieving the file info
            from the provided id({: d}):
               {}
            """.format(file_id, exc)
        )


def set_submission_grader(api_key, submission_id, grader):
    """
    Changes the grader claimed to a submission with a given submission ID.
    To unclaim a submission, set the `grader` to `None`.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    payload = {"grader": grader}

    if grader in [None, "", "None", "null"]:
        payload["grader"] = "" # API requires an empty string to unassign, not null or None

        # A finalized submission must have a grader, so if we are unclaiming, we must also
        # unfinalize.
        payload["isFinalized"] = False

    try:
        r = _requests.patch(
            "{}/submissions/{:d}/".format(BASE_URL, submission_id),
            headers=auth_headers,
            data=payload
        )
        if r.status_code != 200:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return True

    except Exception as exc:
        raise RuntimeError(
            """
            set_submission_grader: Unexpected exception while setting the
            grader of submission with ID {:d} to {}:
               {}
            """.format(submission_id, grader, exc)
        )


def unclaim_submission(api_key, submission_id):
    """
    Unclaims a submission, given the submission ID. This unsets the associated
    grader.
    """
    return set_submission_grader(
        api_key=api_key,
        submission_id=submission_id,
        grader=None
    )


def remove_comments(api_key, submission_id=None, file_id=None):
    """
    Removes all comments either from the submission with the given submission ID
    or from the file with the given file ID.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    # Queue of submissions, files and comments to process
    submissions_to_process = []
    files_to_process = []
    comments_to_delete = []

    # Initialize with provided parameters
    if submission_id != None:
        submissions_to_process.append(submission_id)
    if file_id != None:
        files_to_process.append(file_id)

    # Step 1: Obtain the files of all submissions to process
    for sid in submissions_to_process:
        try:
            r = _requests.get(
                "{}/submissions/{:d}/".format(BASE_URL, sid),
                headers=auth_headers
            )

            if r.status_code == 200:
                files_to_process += r.json().get("files", list())
        except:
            continue

    # Step 2: Obtain the comments for all files to process
    for fid in files_to_process:
        try:
            r = _requests.get(
                "{}/files/{:d}/".format(BASE_URL, fid),
                headers=auth_headers
            )

            if r.status_code == 200:
                comments_to_delete += r.json().get("comments", list())
        except:
            continue

    # Step 3: Remove the comments
    comments_to_delete = set(comments_to_delete)
    total_comments = len(comments_to_delete)
    deleted_comments = 0
    for cid in comments_to_delete:
        try:
            r = _requests.delete(
                "{}/comments/{:d}/".format(BASE_URL, cid),
                headers=auth_headers
            )

            if r.status_code == 204:
                comments_to_delete += r.json().get("comments", list())
                deleted_comments += 1
        except:
            continue

    return (total_comments == deleted_comments)


def delete_submission(api_key, submission_id):
    """
    Deletes the submission with the given submission ID; raises an exception
    if the submission does not exist or cannot be deleted.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    try:
        r = _requests.delete(
            "{}/submissions/{:d}/".format(BASE_URL, submission_id),
            headers=auth_headers
        )

        if r.status_code != 204:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return r.json()

    except Exception as exc:
        raise RuntimeError(
            """
            delete_submission: Unexpected exception while deleting the
            submission with ID {: d}:
               {}
            """.format(submission_id, exc)
        )


def delete_file(api_key, file_id):
    """
    Deletes the file with the given file ID; raises an exception
    if the file does not exist or cannot be deleted.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    try:
        r = _requests.delete(
            "{}/files/{:d}/".format(BASE_URL, file_id),
            headers=auth_headers
        )

        if r.status_code != 204:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return True # no body returned on successful delete

    except Exception as exc:
        raise RuntimeError(
            """
            delete_file: Unexpected exception while deleting the
            file with ID {: d}:
               {}
            """.format(file_id, exc)
        )


def post_file(api_key, submission_id, filename, content, extension):
    """
    Uploads a file to a submission.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    # Build the file payload.
    payload = {
        "submission": submission_id,
        "name": filename,
        "code": content,
        "extension": extension
    }

    try:
        r = _requests.post(
            "{}/files/".format(BASE_URL),
            headers=auth_headers,
            data=payload
        )

        if r.status_code != 201:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return r.json()

    except Exception as exc:
        raise _errors.UploadError(
            message=("""
                post_file: Unexpected exception while uploading the file '{}'
                to submission {: d}:
                {}
                """.format(filename, submission_id, exc)),
            # Additional fields
            api_key=api_key,
            submission_id=submission_id,
        )


def post_submission(api_key, assignment_id, students, files):
    """
    Uploads a submission, give the assignment's ID, and a dictionary containing
    the information on the files to upload.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    # Build the submission payload.
    payload = {
        "assignment": assignment_id,
        "students": students
    }

    submission = None

    # Create the submission
    try:
        r = _requests.post(
            "{}/submissions/".format(BASE_URL),
            headers=auth_headers,
            data=payload
        )

        if r.status_code != 201:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        submission = r.json()

    except Exception as exc:
        submission_id = None if submission == None else submission.get("id", None)
        raise _errors.UploadError(
            message=("""
                post_submission: Unexpected exception while creating a submission
                for students {} for assignment {}:
                {}
                """.format(students, assignment_id, exc)),
            # Additional fields
            api_key=api_key,
            assignment_id=assignment_id,
            submission_id=submission_id,
        )

    # Upload the individual files
    added_file_ids = []
    try:
        for file in files:
            file_obj = post_file(
                api_key=api_key,
                submission_id=submission.get("id"),
                filename=file["name"],
                content=file["code"],
                extension=file["extension"]
            )
            file_id = None if file_obj == None else file_obj.get("id", None)
            if file_id != None:
                added_file_ids.append(file_id)

    except Exception as exc:
        raise _errors.UploadError(
            message=("""
                post_submission: Unexpected exception while adding files to newly
                created submission {}:
                {}
                """.format(submission.get("id"), exc)),
            # Additional fields
            api_key=api_key,
            assignment_id=assignment_id,
            submission_id=submission.get("id"),
            file_ids=added_file_ids,
        )

    return submission

def post_comment(api_key, file, text, pointDelta, startChar, endChar, startLine, endLine, rubricComment=None):
    """
    Adds comment specified by (startChar, endChar, startLine, endLine) to file
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    # Build the comment payload
    payload = {
        "text" : text,
        "pointDelta" : pointDelta,
        "startChar" : startChar,
        "endChar" : endChar,
        "startLine" : startLine,
        "endLine" : endLine,
        "file" : file.get("id", -1) if file else -1, # from arg
    }

    if rubricComment is not None:
        payload["rubricComment"] = rubricComment

    comment = None

    # Create the comment
    try:
        r = _requests.post(
            "{}/comments/".format(BASE_URL),
            headers=auth_headers,
            data=payload
        )

        if r.status_code != 201:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        comment = r.json()

    except Exception as exc:
        raise RuntimeError(
            """
            post_comment: Unexpected exception while creating a comment
            for file with id {}:
               {}
            """.format(payload["file"], exc)
        )

    return comment

def set_submission_students(api_key, submission_id, students):
    """
    Modifies the students associated with a submission.
    """
    # students should be a list of strings
    assert isinstance(students, list)

    auth_headers = {"Authorization": "Token {}".format(api_key)}

    try:
        r = _requests.patch(
            "{}/submissions/{:d}/".format(BASE_URL, submission_id),
            headers=auth_headers,
            data={"students": students}
        )

        if r.status_code != 200:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return r.json()

    except Exception as exc:
        raise RuntimeError(
            """
            set_submission_students: Unexpected exception while updating the
            students({}) associated with submission ID {: d}:
               {}
            """.format(students, submission_id, exc)
        )

def remove_students_from_submission(api_key, submission_info, students_to_remove):
    """
    Removes students from a submission, and possibly delete the submission if no
    user is associated with it anymore.
    """
    # Students to remove should be a list of strings
    assert isinstance(students_to_remove, list)

    new_student_list = list(set(submission_info["students"]).difference(
        set(students_to_remove)))

    if len(new_student_list) == 0:
        # Eliminate orphaned submissions
        return delete_submission(
            api_key=api_key,
            submission_id=submission_info["id"]
        )

    # Update students of this submission
    return set_submission_students(
        api_key=api_key,
        submission_id=submission_info["id"],
        students=new_student_list
    )


def _submission_list_is_unclaimed(submissions):
    for submission in submissions:
        if submission['grader'] is not None:
            return False
    return True

def get_course_grades(api_key, course_name, course_period, only_finalized=True):
    """
    Returns a dictionary mapping every student in the specified course
    to a dictionary, which itself maps assignment names to grades. By
    default, only finalized submission grades are return, but this can
    be changed with the `only_finalized` boolean parameter.
    """
    # Course is an object with these properties:
    # {u'assignments': [92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103],
    #  u'emailNewUsers': True,
    #  u'id': 11,
    #  u'name': u'COS126',
    #  u'organization': 1,
    #  u'period': u'S2019',
    #  u'sections': [64, 65, 66, 67, 68, 69, 70, 71, 89, 90, 91, 92, 93, 94, 95],
    #  u'sendReleasedSubmissionsToBack': True,
    #  u'showStudentsStatistics': True,
    #  u'timezone': u'US/Eastern'}

    course = get_course_roster_by_name(
        api_key=api_key,
        course_name=course_name,
        course_period=course_period)

    # Mapping:  student -> (assignment -> grade)
    # This data structure is optimizing storing for output
    grades = {}

    for aid in course["assignments"]:

        # Assignment object:
        # {u'course': 11,
        #  u'id': 92,
        #  u'isReleased': True,
        #  u'mean': 19.49,
        #  u'median': 20.0,
        #  u'name': u'Loops',
        #  u'points': 20,
        #  u'rubricCategories': [519, 640, 641, 642, 643, 644, 645],
        #  u'sortKey': 1}
        assignment_info = get_assignment_info_by_id(
            api_key=api_key,
            assignment_id=aid)

        assignment_name = assignment_info["name"]

        # Submission object:
        # {u'assignment': 92,
        #  u'dateEdited': u'2019-02-20T22:55:55.335293-05:00',
        #  u'files': [40514, 40515, 40516, 40517, 40518, 40519, 40520],
        #  u'grade': 20.0,
        #  u'grader': u'jgrader@princeton.edu',
        #  u'id': 9351,
        #  u'isFinalized': True,
        #  u'queueOrderKey': 1,
        #  u'students': [u'jstudent@princeton.edu']}
        submissions = get_assignment_submissions(
            api_key=api_key,
            assignment_id=aid)

        for submission in submissions:


            # Ungraded
            if submission.get("grade", None) == None:
                continue

            # Unclaimed
            if submission.get("grader", None) == None:
                continue

            # Unfinalized
            if submission.get("isFinalized", False) == False:
                if only_finalized:
                    continue

            # Insert the grade in our data structure
            for student in submission.get("students", list()):
                student_grades = grades.get(student, dict())
                student_grades[assignment_name] = submission["grade"]
                grades[student] = student_grades

    # At this point, grades contains all the grades of the assignments
    # of the course

    return grades
