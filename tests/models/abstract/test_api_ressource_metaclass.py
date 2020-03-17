
import collections
import typing

import pytest

import codepost.models.abstract.api_resource_metaclass as _arm


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
