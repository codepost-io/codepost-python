# codePost API Python SDK

[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/codepost-python/community)
[![Build Status](https://travis-ci.com/codepost-io/codePost-python.svg?branch=master)](https://travis-ci.com/codepost-io/codePost-python?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/codepost-io/codepost-python/badge.svg?branch=master)](https://coveralls.io/github/codepost-io/codepost-python?branch=master)

This package provides a Python library to conveniently access the codePost API
from any application or script written in the Python language.

You can learn more about [codePost](https://codepost.io), the best tool for educational code feedback, or
check out the documentation for powerful, best-in-class [REST API](https://docs.codepost.io/reference) that
this Python SDK allows you to control.

You can also dive in directly with the [codePost API Python SDK cheatsheet](https://docs.codepost.io/docs/python-sdk-cheatsheet).

# Quickstart

This section provides a quick overview of how to install the library and getting started, for more complete
information, you can reference our [First Steps with the codePost API Python
SDK](https://docs.codepost.io/docs/first-steps-with-the-codepost-python-sdk).


1. This codePost API Python SDK is available on the Python package manager PyPi, and can be installed from all
usual sources, such as with `pip`:
    ```shell
    sudo pipenv install codepost
    ```
    You can also install the package just for your account (`pip install --user codepost`) or using a tool such
    as `pipenv` which will install the library in a virtual environment (`pipenv install codepost`). 
2. Once you've import the `codepost` package, you need to configure it with the API key you've obtained
    from [your Settings page](https://codepost.io/settings) 
    (for other means of setting the API key,
    [read here](https://docs.codepost.io/docs/first-steps-with-the-codepost-python-sdk)):
    ```python
    import codepost
    codepost.configure_api_key("ddafde24389de98434f8df3ee482389de98432afde24482f3428923491344f8df3eef34892349134")
    ```
3. You can then directly access the codePost objects:
    ```python
    course = codepost.course.list_available(name="CS101", period="Spring 2020")[0]
    assignment = course.assignments.by_name("Hello World")
    submissions = assignment.list_submissions()
    for submission in submissions:
        print("{student},{grade}", student="+".join(submission.students), grade=submission.grade)
    ```
    to print the grades of all submissions of the assignment `"Hello World"` of the course CS101 in Spring 2020.

# Development

The codePost API Python SDK is under active development. At this time, we are welcoming all
issues, suggestions and feature requests. Please either [post a GitHub issue on this
repository](https://github.com/codepost-io/codepost-python/issues), or [join our Gitter
channel](https://gitter.im/codepost-python/community) to ask a question.


## Running tests

To start developing, install [pipenv](https://github.com/pypa/pipenv), then install
all dependencies (including development dependencies, with the flag `--dev`) for this project:
    
    git clone https://github.com/codepost-io/codepost-python
    cd codepost-python
    pipenv install --dev

Run all tests on all supported versions of Python which you have locally installed:

    make test

Run all tests for a specific Python version (modify `-e` according to your Python target):

    pipenv run tox -e py37

Run all tests in a single file for a specific Python version:

    pipenv run tox -e py37 -- tests/util/test_misc.py