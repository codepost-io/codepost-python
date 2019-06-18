#!/usr/bin/env python3
##########################################################################
# codePost error/exception classes
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

####################
# Local dependencies
#
from . import util as _util

##########################################################################


_logger = _util.get_logger(__name__)

##########################################################################


class UploadError(RuntimeError):

    def __init__(self, message="",
        api_key=None, assignment_id=None, submission_id=None,
        file_ids=None, *args, **kwargs):

        super(UploadError, self).__init__(message, *args, **kwargs)

        self.api_key = api_key
        self._assignment_id = assignment_id

        # Initialize object lists
        self._submission_ids = (
            [] if submission_id == None else [ submission_id ])
        self._file_ids = [] if file_ids == None else file_ids

        # Trace of operations undertaken by the cleanup method
        self._trace = ""

    def force_cleanup(self):
        """
        Delete submissions and/or files created during a transaction
        with codePost that had to be reverted because of an error.
        """
        self._trace += "<<"

        # NOTE: We manually delete the models bottom-up (comments ->
        # files -> submissions), to provide the user with a log of the
        # objects that have been affected. However, because the database
        # enforces relationship constraints, it would be sufficient to
        # delete the top-most model, i.e., a call to delete the
        # submission will delete all its orphaned child objects.

        from . import helpers

        for f_id in self._file_ids:
            try:
                helpers.delete_file(
                    api_key=self.api_key, file_id=f_id)
            except:
                self._trace += "!file({}); ".format(f_id)
            else:
                self._trace += "-file({}); ".format(f_id)

        for s_id in self._submission_ids:
            try:
                helpers.delete_submission(
                    api_key=self.api_key, submission_id=s_id)
            except:
                self._trace += "!submission({}); ".format(s_id)
            else:
                self._trace += "-submission({}); ".format(s_id)

        self._trace += ">>"

        return self._trace

##########################################################################
