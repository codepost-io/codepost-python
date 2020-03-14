
import copy

import pytest

import codepost.util.misc as _misc


class _StringableErr:
    """
    Class intended to fail when converted to string, or printed.
    """

    def __str__(self):
        raise Exception("intended")

    def __repr__(self):
        raise Exception("intended")


class TestIsStringable:
    """
    Tests for the `codepost.util.misc.is_stringable` method.
    """

    ANY_NUMBER = 1
    ANY_STRING = "AAAA"

    def test_true_with_int_input(self):
        assert _misc.is_stringable(self.ANY_NUMBER)

    def test_true_with_str_input(self):
        assert _misc.is_stringable(self.ANY_STRING)

    def test_false(self):
        bad_obj = _StringableErr()
        assert not _misc.is_stringable(bad_obj)


class TestIsNoargCallable:
    """
    Tests for the `codepost.util.misc.is_noarg_callable` method.
    """

    def test_true(self):
        good_obj = lambda: True
        assert _misc.is_noarg_callable(good_obj)

    def test_false(self):

        # this mock function throws an exception
        bad_obj = lambda: 0/0

        assert not _misc.is_noarg_callable(bad_obj)


class TestRobustStr:
    """
    Tests for the `codepost.util.misc.robust_str` method.
    """

    DEFAULT_STRING = "N/A"

    ANY_NUMBER = 1
    ANY_STRING = "AAAA"

    ANY_NUMBER_STR = "1"
    ANY_STRING_STR = "AAAA"

    def test_true_with_int_input(self):
        assert _misc.robust_str(
            obj=self.ANY_NUMBER,
            default=self.DEFAULT_STRING) == self.ANY_NUMBER_STR

    def test_true_with_str_input(self):
        assert _misc.robust_str(
            obj=self.ANY_STRING,
            default=self.DEFAULT_STRING) == self.ANY_STRING_STR

    def test_false(self):
        bad_obj = _StringableErr()
        assert _misc.robust_str(
            obj=bad_obj,
            default=self.DEFAULT_STRING) == self.DEFAULT_STRING

    def test_default(self):
        bad_obj = _StringableErr()
        assert _misc.robust_str(obj=bad_obj) == self.DEFAULT_STRING


class TestIsFieldSetInKwargs:
    """
    Tests for the `codepost.util.misc.is_field_set_in_kwargs` method.
    """

    SOME_FIELD_NAME = "fieldname1"
    SOME_FIELD_VALUE = "field value 1"
    SOME_ABSENT_FIELD_NAME = "fieldname2"
    SOME_DICT = { SOME_FIELD_NAME: SOME_FIELD_VALUE, }

    def test_absent(self):
        obj = copy.copy(self.SOME_DICT)
        assert not _misc.is_field_set_in_kwargs(field=self.SOME_ABSENT_FIELD_NAME, kwargs=obj)

    def test_present_but_void(self):
        # obtain FORGE void
        import codepost.models.abstract.api_resource_metaclass as _arm

        # succeed if forge not active (since this test is not relevant)
        if not _arm._forge:
            assert True
            return

        obj = {self.SOME_FIELD_NAME: _arm._FORGE_VOID}

        assert not _misc.is_field_set_in_kwargs(field=self.SOME_FIELD_NAME, kwargs=obj)

    def test_present(self):
        # obtain FORGE void
        import codepost.models.abstract.api_resource_metaclass as _arm

        # succeed if forge not active (since this test is not relevant)
        if not _arm._forge:
            assert True
            return

        obj = copy.copy(self.SOME_DICT)

        assert _misc.is_field_set_in_kwargs(field=self.SOME_FIELD_NAME, kwargs=obj)


class TestMakeF:
    """
    Tests for the `codepost.util.misc._make_f` method factory.
    """

    SOME_FIELD_NAME = "fieldname1"
    SOME_FIELD_VALUE = "field value 1"
    SOME_FIELD_VALUE_ALTERNATE = "field value 1 alternate"
    SOME_ABSENT_FIELD_NAME = "fieldname2"
    SOME_DICT = {SOME_FIELD_NAME: SOME_FIELD_VALUE}
    SOME_DICT_ALTERNATE = {SOME_FIELD_NAME: SOME_FIELD_VALUE_ALTERNATE}
    SOME_EMPTY_DICT = dict()

    SOME_FORMAT_STRING_NO_KEY = "format_string_no_key"
    SOME_FORMAT_STRING_WITH_KEY_REMOVED = "format_string_with_key_"
    SOME_FORMAT_STRING_WITH_KEY = "{}{{{}}}".format(
        SOME_FORMAT_STRING_WITH_KEY_REMOVED, SOME_FIELD_NAME)
    SOME_FORMAT_STRING_WITH_KEY_REPLACED = SOME_FORMAT_STRING_WITH_KEY_REMOVED + SOME_FIELD_VALUE
    SOME_FORMAT_STRING_CAUSING_VALUE_ERROR = "{{}"

    def factory_make_empty_f(self):
        """
        Helper function to create a formatting function with empty dictionaries.
        """
        return _misc._make_f(self.SOME_EMPTY_DICT, self.SOME_EMPTY_DICT)

    def test_no_key_no_dict(self):
        f = self.factory_make_empty_f()
        return f(self.SOME_FORMAT_STRING_NO_KEY) == self.SOME_FORMAT_STRING_NO_KEY

    def test_no_key_dict(self):
        f = self.factory_make_empty_f()
        return f(self.SOME_FORMAT_STRING_NO_KEY, self.SOME_DICT) == self.SOME_FORMAT_STRING_NO_KEY

    def test_value_error(self):
        f = self.factory_make_empty_f()
        return f(self.SOME_FORMAT_STRING_NO_KEY) == self.SOME_FORMAT_STRING_NO_KEY

    def test_missing_key_with_remain(self):
        f = self.factory_make_empty_f()
        return f(self.SOME_FORMAT_STRING_WITH_KEY,
                 missing=_misc.MissingFormatKey.REMAIN) == self.SOME_FORMAT_STRING_WITH_KEY

    def test_missing_key_with_error(self):
        f = self.factory_make_empty_f()
        with pytest.raises(KeyError):
            f(self.SOME_FORMAT_STRING_WITH_KEY, missing=_misc.MissingFormatKey.ERROR)

    def test_missing_key_with_removed(self):
        f = self.factory_make_empty_f()
        return f(self.SOME_FORMAT_STRING_WITH_KEY,
                 missing=_misc.MissingFormatKey.REMOVE) == self.SOME_FORMAT_STRING_WITH_KEY_REMOVED

    def test_missing_key_default(self):
        # by default behave like REMAIN
        f = self.factory_make_empty_f()
        return f(self.SOME_FORMAT_STRING_WITH_KEY) == self.SOME_FORMAT_STRING_WITH_KEY

    def test_value_error(self):
        # by default behave like REMAIN
        f = self.factory_make_empty_f()
        with pytest.raises(ValueError):
            f(self.SOME_FORMAT_STRING_CAUSING_VALUE_ERROR)

    def test_key_subbed_from_globals(self):
        f = _misc._make_f(self.SOME_DICT, self.SOME_EMPTY_DICT)
        return f(self.SOME_FORMAT_STRING_WITH_KEY) == self.SOME_FORMAT_STRING_WITH_KEY_REPLACED

    def test_key_subbed_from_locals(self):
        f = _misc._make_f(self.SOME_EMPTY_DICT, self.SOME_DICT)
        return f(self.SOME_FORMAT_STRING_WITH_KEY) == self.SOME_FORMAT_STRING_WITH_KEY_REPLACED

    def test_key_subbed_from_args(self):
        f = _misc._make_f(self.SOME_EMPTY_DICT, self.SOME_EMPTY_DICT)
        return f(self.SOME_FORMAT_STRING_WITH_KEY,
                 **self.SOME_DICT) == self.SOME_FORMAT_STRING_WITH_KEY_REPLACED

    def test_key_subbed_from_args_over_globals(self):
        f = _misc._make_f(self.SOME_DICT_ALTERNATE, self.SOME_EMPTY_DICT)
        return f(self.SOME_FORMAT_STRING_WITH_KEY,
                 **self.SOME_DICT) == self.SOME_FORMAT_STRING_WITH_KEY_REPLACED

    def test_key_subbed_from_args_over_locals(self):
        f = _misc._make_f(self.SOME_EMPTY_DICT, self.SOME_DICT_ALTERNATE)
        return f(self.SOME_FORMAT_STRING_WITH_KEY,
                 **self.SOME_DICT) == self.SOME_FORMAT_STRING_WITH_KEY_REPLACED
