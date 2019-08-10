# =============================================================================
# codePost v2.0 SDK
#
# LINKED LISTS WRAPPER SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Local imports
import codepost
import codepost.models.abstract.api_resource as _api_resource
import codepost.models.abstract.lazy as _lazy

# =============================================================================

class APILinkedList(list):
    """
    Base class
    """

    _cls = None
    _parent_cls = None
    _parent_id = None
    _parent_attribute = None
    _query_attribute = None
    _deleted = None

    def _misc_to_internal_iterable(self, iterable):
        return iterable

    def __init__(
            self,
            iterable=(),
            cls=None,
            parent_cls=None,
            parent_id=None,
            parent_attribute=None,
            query_attribute="name"
    ):
        # Configure the class
        self._cls = cls

        # Preprocess the iterable
        iterable = self._misc_to_internal_iterable(iterable)

        # Pass it to parent constructor
        super(APILinkedList, self).__init__(iterable)

        # Continue configuration
        self._parent_cls = parent_cls
        self._parent_id = parent_id
        self._parent_attribute = parent_attribute

        self._query_attribute = query_attribute
        self._deleted = list()

    def _to_serializable_list(self, lst=None):
        if lst is None:
            lst = self

        return list(lst)

    def _cleanup_list(self):
        return self

    def by_name(self, name):
        if name is None:
            return []

        return [
            item
            for item in self
            if getattr(item, self._query_attribute, None) == name
        ]

    def append(self, value):
        return self.__add__([value])

    def __add__(self, value, *args):
        self._added = getattr(self, "_deleted", list())

        new_list = self._misc_to_internal_iterable(
            iterable=([value] + args)
        )

        try:
            obj = super(APILinkedList, self).__add__(new_list)
            self._added += self._to_serializable_list(lst=new_list)
            return obj
        except:
            raise

    def __delitem__(self, key):
        self._deleted = getattr(self, "_deleted", list())

        try:
            _id = None
            if self._cls is not None:
                _id = self[key].id

            super(APILinkedList, self).__delitem__(key)

            if self._cls is not None:
                self._deleted.append(_id)
        except:
            raise

    def save(self):

        # Make the deletion by calling `delete` in the child class
        if self._cls is not None:

            static_helper = self._cls()
            for obj_id in set(self._deleted):
                try:
                    static_helper.delete(id=obj_id)
                except:
                    continue
            self._deleted = list()

        # Synchronize the field in the parent
        if not (
                self._parent_cls is None or
                self._parent_id is None or
                self._parent_attribute is None
        ):
            # Convert the list into a serializable list
            objs_serializable_list = self._to_serializable_list()

            # Payload
            data = {
                self._parent_attribute: objs_serializable_list
            }

            # Instantiate a static object to manipulate parent class
            obj = self._parent_cls().update(id=self._parent_id, **data)

            # Refresh fields
            new_parent_list = getattr(obj, "_data", dict()).get(
                self._parent_attribute,
                list()
            )

            # Preprocess the iterable
            iterable = self._misc_to_internal_iterable(new_parent_list)

            # Pass it to parent constructor
            return super(APILinkedList, self).__init__(iterable)


# =============================================================================

class LazyAPILinkedList(APILinkedList):

    @staticmethod
    def _is_lazy(obj):
        try:
            is_lazy = "_inner" in obj.__class__.__dict__
            return is_lazy
        except:
            return False

    @staticmethod
    def _is_lazy_null(obj):
        try:
            is_lazy = "_inner" in obj.__class__.__dict__
            is_null = getattr(obj, "_null", False)
            return is_lazy and is_null
        except:
            return False

    def _misc_to_internal_iterable(self, iterable):
        return map(lambda obj: obj
        if LazyAPILinkedList._is_lazy(obj)
        else _lazy.create_lazy_resource(cls=self._cls, id=obj), iterable)

    def _to_serializable_list(self, lst=None):
        if lst is None:
            lst = self

        id_list = list(map(
            lambda obj: obj.id,
            lst
        ))

        return id_list

    def _cleanup_list(self):

        i = 0

        while i < len(self):
            obj = self[i]

            if LazyAPILinkedList._is_lazy_null(obj):
                super(LazyAPILinkedList, self).__delitem__(i)
                continue

            if not LazyAPILinkedList._is_lazy(obj):
                try:
                    new_obj = _lazy.create_lazy_resource(
                        cls=self._cls,
                        id=obj
                    )
                    self[i] = new_obj
                except:
                    super(LazyAPILinkedList, self).__delitem__(i)
                    continue

            i += 1

# =============================================================================

