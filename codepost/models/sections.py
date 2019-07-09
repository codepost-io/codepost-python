# =============================================================================
# codePost v2.0 SDK
#
# COMMENT MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing

# Local imports
from . import abstract as _abstract

# =============================================================================

class Sections(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
    metaclass=_abstract.APIResourceMetaclass
):
    _OBJECT_NAME = "sections"
    _FIELD_ID = "id"
    _FIELDS = {
        'name': (str, 'The name of the section.'),
        'course': (int, 'ID of the Course which this Section belongs to.'),
        'leaders': (object, 'The graders who lead this section.'),
        'students': (object, 'The student members of this section.')
    }
    _FIELDS_READ_ONLY = []
    _FIELDS_REQUIRED = [ "name", "course", "leaders", "students" ]

# =============================================================================
