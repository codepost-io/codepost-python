
import collections
import typing
import sys

import pytest

import codepost.models.abstract.api_resource_metaclass as _arm

TARGET_MODULE = "codepost.models.abstract.api_resource_metaclass"

FixtureTestData = collections.namedtuple(
    'FixtureTestData',
    ['input', 'output'])


class BogusClass:
    pass


class TestDetectListType:
    """
    Testing class for `codepost.models.abstract.api_resource_metaclass`
    method `detect_list_type`.
    """

    test_data = [
        FixtureTestData(int, None),
        FixtureTestData(str, None),
        FixtureTestData(typing.List[int], int),
        FixtureTestData(typing.List[str], str),
        FixtureTestData(typing.List[BogusClass], BogusClass),
        FixtureTestData(BogusClass, None)
    ]

    test_ids = [
        "{input} => {output}".format(
            input=test_datum.input, output=test_datum.output,
        )
        for test_datum in test_data
    ]

    @pytest.mark.parametrize("test_data", test_data, ids=test_ids)
    def test_correctness(self, test_data):
        assert _arm.detect_list_type(test_data.input) == test_data.output

    def test_py37_above(self, mocker):
        target_typ = int

        mocker.patch("{}._sys".format(TARGET_MODULE), version_info=(3, 7))

        built_typ = mocker.patch(
            "{}._typing._GenericAlias".format(TARGET_MODULE),
            create=True, _name="List", __args__=[target_typ])

        if sys.version_info >= (3, 0):
            mocker.patch("builtins.type", create=True, return_value=built_typ)
        else:
            mocker.patch("__builtin__.type", create=True, return_value=built_typ)

        assert _arm.detect_list_type(built_typ) == target_typ

    def test_py30_to_36(self, mocker):
        target_typ = int

        mocker.patch("{}._sys".format(TARGET_MODULE), version_info=(3, 0))

        built_typ = mocker.patch(
            "{}._typing.GenericMeta".format(TARGET_MODULE),
            create=True, __extra__=list, __args__=[target_typ])

        mocker.patch("{}.type".format(TARGET_MODULE), return_value=built_typ)

        assert _arm.detect_list_type(built_typ) == target_typ

    def test_py30_to_36_with_type_exception(self, mocker):
        target_typ = int

        mocker.patch("{}._sys".format(TARGET_MODULE), version_info=(3, 0))

        built_typ = mocker.patch(
            "{}._typing.GenericMeta".format(TARGET_MODULE),
            create=True, __origin__=typing.List, __args__=[target_typ])

        mocker.patch("{}.type".format(TARGET_MODULE), side_effect=AttributeError())

        assert _arm.detect_list_type(built_typ) == target_typ



class TestIsTypeVariable:
    """
    Testing class for `codepost.models.abstract.api_resource_metaclass`
    method `is_type_variable`.
    """

    test_data = [
        # types
        FixtureTestData(int, True),
        FixtureTestData(str, True),
        FixtureTestData(typing.List[int], True),
        FixtureTestData(typing.List[str], True),
        FixtureTestData(typing.List[BogusClass], True),
        FixtureTestData(BogusClass, True),

        # data
        FixtureTestData(1, False),
        FixtureTestData("str", False),
        FixtureTestData("BogusClass", False),
        FixtureTestData([1, 2, 3], False),
    ]

    test_ids = [
        "{input} => {output}".format(
            input=test_datum.input, output=test_datum.output,
        )
        for test_datum in test_data
    ]

    @pytest.mark.parametrize("test_data", test_data, ids=test_ids)
    def test_correctness(self, test_data):
        assert _arm.is_type_variable(test_data.input) == test_data.output

    def test_py37_above(self, mocker):
        target_typ = int

        mocker.patch("{}._sys".format(TARGET_MODULE), version_info=(3, 7))

        built_typ = mocker.patch(
            "{}._typing._GenericAlias".format(TARGET_MODULE),
            create=True, _name="List", __args__=[target_typ])

        if sys.version_info >= (3, 0):
            mocker.patch("builtins.type", create=True, return_value=built_typ)
        else:
            mocker.patch("__builtin__.type", create=True, return_value=built_typ)

        assert _arm.is_type_variable(built_typ)

    def test_py30_to_36(self, mocker):
        target_typ = int

        mocker.patch("{}._sys".format(TARGET_MODULE), version_info=(3, 0))

        built_typ = mocker.patch(
            "{}._typing.GenericMeta".format(TARGET_MODULE),
            create=True, __extra__=list, __args__=[target_typ])

        mocker.patch("{}.type".format(TARGET_MODULE), return_value=built_typ)

        assert _arm.is_type_variable(built_typ)

    def test_py30_to_36_with_type_exception(self, mocker):
        target_typ = int

        mocker.patch("{}._sys".format(TARGET_MODULE), version_info=(3, 0))

        built_typ = mocker.MagicMock(__origin__=typing.List, __args__=[target_typ])

        assert _arm.is_type_variable(built_typ)

    def test_py2(self, mocker):
        mocker.patch("{}._sys".format(TARGET_MODULE), version_info=(2, 7))
        assert not _arm.is_type_variable(None)
