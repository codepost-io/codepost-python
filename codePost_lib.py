#!/usr/bin/env python3
##########################################################################
# codePost submission utils
#
# DATE:    2019-02-12
# AUTHOR:  codePost (team@codepost.io)
#
##########################################################################

import sys as _sys
import requests as _requests

try:
    # Python 2
    from urllib import quote as _urlquote
except ImportError:
    # Python 3
    from urllib.parse import quote as _urlquote

BASE_URL = 'https://api.codepost.io'

##########################################################################


class _color:
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


_TERM_INFO = "{END}[{BOLD}INFO{END}]{END}".format(**_color.__dict__)
_TERM_ERROR = "{END}[{BOLD}{RED}ERROR{END}]{END}".format(**_color.__dict__)


def _print_info(msg):
    print("{tag} {msg}".format(tag=_TERM_INFO, msg=msg), file=_sys.stderr)


DEFAULT_MODE = {
    "updateIfExists": True,
    "updateIfClaimed": True,
    "resolveStudents": True,
    "addFiles": True,
    "updateExistingFiles": True,
    "removeComments": True,
    "doUnclaim": True,
    "deleteAffectedSubmissions": True
}

###########################################################################################


###########################################################################################

def get_available_courses(api_key, course_name=None, course_period=None):
    """
    Returns a list of the available courses/terms to which the user, associated with
    the provided API key, has access to. Optionally, restrict the results to a specific
    course and/or period.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    result = None

    try:
        r = _requests.get(
            "{}/users/me".format(BASE_URL),
            headers=auth_headers
        )

        if r.status_code != 200:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        result = r.json().get("courseadminCourses", list())

    except Exception as exc:

        raise RuntimeError(
            """
            get_available_courses: Unexpected exception while retrieving the list
            of available courses/terms; this could be related to the API key ({:.5})
            being either unavailable, invalid, or stale:
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
            assignment info from the provided id ({:d}):
               {}
            """.format(assignment_id, exc)
        )


def get_assignment_info_by_name(api_key, course_name, course_period, assignment_name):
    """
    Returns the assignment information dictionary, given a (course name, course period,
    assignment name) tuple. This contains, in particular, the ID of the assignment that
    is considered.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

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
            get_assignment_info: Either no course with the specified course ({})
            and period ({}) exists, or the provided API key ({:.5}...) does not have
            access to it.
            """.format(course_name, course_period, api_key)
        )

    elif len(courses) > 1:
        raise RuntimeError(
            """
            get_assignment_info: Request the provided course name ({}) and
            period ({}) resulted in more than one result ({}).
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


def get_assignment_submissions(api_key, assignment_id, username=None):
    """
    Returns the list of submissions of an assignment, provided an assignment ID
    and, optionally, a username.
    """

    auth_headers = {"Authorization": "Token {}".format(api_key)}

    result = None

    try:
        request_url = "{}/assignments/{}/submissions".format(
            BASE_URL,
            assignment_id
        )

        if username != None:
            # Filter according to a specific student
            request_url += "?student={}".format(_urlquote(username))

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
        if username != None:
            student_msg = " associated with student '{}'".format(
                _urlquote(username))

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


def delete_submission(api_key, submission_id):
    """
    Deletes the submission with the given submission ID; raises an exception
    if the submission does not exist or cannot be deleted.
    """
    auth_headers = {"Authorization": "Token {}".format(api_key)}

    try:
        r = _requests.get(
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
            submission with ID {:d}:
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
        r = _requests.get(
            "{}/files/{:d}/".format(BASE_URL, file_id),
            headers=auth_headers
        )

        if r.status_code != 204:
            raise RuntimeError("HTTP request returned {}: {}".format(
                r.status_code, r.content))

        return r.json()

    except Exception as exc:
        raise RuntimeError(
            """
            delete_file: Unexpected exception while deleting the
            file with ID {:d}:
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
        raise RuntimeError(
            """
            post_file: Unexpected exception while uploading the file '{}'
            to submission {:d}:
               {}
            """.format(filename, submission_id, exc)
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
        raise RuntimeError(
            """
            post_submission: Unexpected exception while creating a submission
            for students {} for assignment {}:
               {}
            """.format(students, assignment_id, exc)
        )

    # Upload the individual files
    try:
        for file in files:
            post_file(
                api_key=api_key,
                submission_id=submission.get("id"),
                filename=file["name"],
                content=file["code"],
                extension=file["extension"]
            )

    except Exception as exc:
        raise RuntimeError(
            """
            post_submission: Unexpected exception while adding files to newly
            created submission {}:
               {}
            """.format(submission.get("id"), exc)
        )

    return submission


def set_submission_students(api_key, submission_id, students):
    """
    Modifies the students associated with a submission.
    """
    # students should be a list of strings
    assert isinstance(students_to_remove, students)

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
            students ({}) associated with submission ID {:d}:
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
