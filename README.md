# codePost Python Library

The codePost Python library provides a set of helper functions used to access the codePost API from applications written in the Python language. This repo also includes a command-line utility (`upload-to-codePost`) which utilizes the codePost Python library to provide language-agnostic access to a submission upload service. 

## Documentation

Check out the [Python API docs](http://docs.codepost.io/?python#introduction).

## Installation

__To fill in once library is publicly available.__

## Usage
To use the functions available in `codePost_lib.py`, you must have a codePost API key. To retrieve an API key, you must be a admin of a course on codePost. You can do so at [https://codepost.io/settings](https://codepost.io/settings).

## Command Line Syntax
```
> ./upload-to-codePost --help
usage: upload-to-codePost [-h] [-api_key API_KEY] [-course_name COURSE_NAME]
                          [-course_period COURSE_PERIOD]
                          [-assignment_name ASSIGNMENT_NAME]
                          [-students STUDENTS] [-files FILES [FILES ...]]
                          [--extend] [--overwrite]

optional arguments:
  -h, --help                            show this help message and exit
  -api_key API_KEY                      the API key to authenticate upload
  -course_name COURSE_NAME              the name of the course to upload to (e.g. COS126)
  -course_period COURSE_PERIOD          the period of the course to upload to (e.g. S2019)
  -assignment_name ASSIGNMENT_NAME      the name of the assignment to upload to (e.g. Loops)
  -students STUDENTS                    comma-separated list of student emails
  -files FILES [FILES ...]              comma-separated list of file paths
  --extend                              If submission already exists, add new files to it and
                                        replace old files if the code has changed.
  --overwrite                           If submission already exists, overwrite it.
  ```
