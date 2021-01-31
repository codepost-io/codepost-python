# =============================================================================
# codePost v2.0 SDK
#
# LOGGING SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import logging as _logging
import os as _os
import time as _time
import sys as _sys
import platform as _platform

# External imports
# import better_exceptions as _better_exceptions
import eliot
import eliot.stdlib

# Eliot imports
from eliot import Message
from eliot import log_call, start_task
from eliot import start_action, current_action, Action

# =============================================================================

# Global submodule constants
LOG_FILENAME = "codepost.log"
LOG_DEFAULT_SCOPE = "{}".format(__name__)
LOG_FILE = open(LOG_FILENAME, "ab")

# Global submodule protected attributes
_logger = None
_only_eliot = False
_eliot_configured = False
_loggers_configured = {}

# =============================================================================

def fail_action(reason="", warning=True):
    # type: (str, bool) -> None
    """
    Helper method to report an `eliot` action as failed.
    """
    exc_klass = RuntimeError
    if warning:
        exc_klass = RuntimeWarning

    return current_action().finish(exception=exc_klass(reason))

# =============================================================================

class _QuietableStreamHandler(_logging.StreamHandler):
    """
    Wrapper around the `logging.StreamHandler` that can be toggled through the
    global submodule attribute `_only_eliot`.
    """

    def setLevel(self, lvl, *args, **kwargs):
        """
        Set the logging level of this logger.  level must be an int or a str.
        """
        return super(_QuietableStreamHandler, self).setLevel(
            lvl, *args, **kwargs)

    def emit(self, record, *args, **kwargs):
        """
        Emit a record, but only if the global submodule attribute `_only_eliot`
        is `False`.
        """
        if not _only_eliot:
            return super(_QuietableStreamHandler, self).emit(
                record, *args, **kwargs)

# =============================================================================

class _SimpleColorFormatter(_logging.Formatter):
    """
    This is a simple log formatting class to output short informative users to
    the console, for the benefit of the end-user. This is complementary to the
    more serious logging effort with the `eliot` library.
    """

    def __init__(self, *args, **kwargs):
        """
        Configure the formatter by initializing the colored terminal captions,
        for the log events which are output to standard output.
        """
        import blessings as _blessings
        _t = _blessings.Terminal()
        f = lambda s: s.format(_t=_t) # Python 2 compatibility of f"..."
        self._title = {
            "DEBUG":   f("{_t.normal}[{_t.bold}{_t.blue}DBUG{_t.normal}]"),
            "INFO":    f("{_t.normal}[{_t.bold}{_t.green}INFO{_t.normal}]"),
            "WARNING": f("{_t.normal}[{_t.bold}{_t.yellow}WARN{_t.normal}]"),
            "ERROR":   f("{_t.normal}[{_t.bold}{_t.red}ERR.{_t.normal}]"),
        }
        super(_SimpleColorFormatter, self).__init__(*args, **kwargs)

    def normalize_path(self, path):
        # type: str -> str
        """
        Return a path which is relative to the working directory, provided a
        path that may be absolute or relative (for error reporting).
        """
        abs_path = _os.path.abspath(path)
        pwd_path = _os.getcwd()
        return abs_path.replace(pwd_path, ".", 1)

    def format_message(self, record):
        # type: (_logging.LogRecord) -> str
        """
        Format a log record as provided by the standard `logging` library, to
        have color characters for terminal output.
        """
        header = self._title.get(record.levelname, self._title.get("INFO"))
        return("{} {} (\"{}\", line {}): {}".format(
            header,
            record.module,
            self.normalize_path(record.filename),
            record.lineno,
            record.message
        ))

    def formatMessage(self, record):
        # type: (_logging.LogRecord) -> str
        return self.format_message(record=record)

# =============================================================================

def _setup_eliot():
    # type: () -> bool
    """
    Set up the `eliot` package so that it outputs to a log file.
    """

    global _eliot_configured

    if not _eliot_configured:
        eliot.to_file(LOG_FILE)
        _eliot_configured = True

    return _eliot_configured

def _setup_logging(name=None, level="INFO"):
    # type: (str, str) -> _logging.Logger
    """
    Set up the logger for a specific submodule.
    """

    logger = _logging.getLogger(name)

    # Check if we have already configured this logger.

    if not name in _loggers_configured:

        # Add the color handler to the terminal output

        handler = _logging.StreamHandler()#_QuietableStreamHandler()

        if _platform.system() != 'Windows':
            formatter = _SimpleColorFormatter()
            handler.setFormatter(formatter)

        # Set logging level of the terminal output (default to provided level)

        handler.setLevel(_os.environ.get("LOGLEVEL", level))

        # Set logging level of the logger

        logger.setLevel("DEBUG")

        # Add the color terminal output handler to the logger

        logger.addHandler(handler)

        # Add the EliotHandler so that all user-intended prompts are also
        # logged in the master log; we set the level to DEBUG so all messages
        # are logged.

        eliotHandler = eliot.stdlib.EliotHandler()
        eliotHandler.setLevel("DEBUG")
        logger.addHandler(eliotHandler)

        # Remember we configured this logger

        _loggers_configured[name] = handler

        # We may also need to configure eliot (at most once)

        _setup_eliot()

    return logger

# =============================================================================

def get_logger(name=None):
    # type: (str) -> _logging.Logger
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    global _logger

    if name == None or name == "":

        # Configure it the first time
        if _logger == None:
            _logger = _setup_logging(LOG_DEFAULT_SCOPE)

        return _logger
    else:
        return _setup_logging(name)

# =============================================================================

def make_verbose():
    # type: () -> bool
    """
    Make the logging verbose by output the full `eliot` output.
    """
    global _only_eliot

    if not _only_eliot:
        # Change the attribute (which will mute normal standard error msgs)
        _only_eliot = True

        # Add a standard output stream to eliot
        eliot.to_file(_sys.stdout)

    return _only_eliot

# =============================================================================
