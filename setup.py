from codepost import __version__
from setuptools import setup, find_packages

# The text of the README file
README = open("README.md").read()

# This call to setup() does all the work
setup(
    name="codepost",
    version=__version__,
    description="Python bindings for the codePost API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/codepost-io/codepost-python",
    author="codePost",
    author_email="team@codepost.io",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    install_requires=[
        "requests",
        "PyYAML",
        "better_exceptions",
        "blessings",
        "colorama",
        "eliot",
        "python_forge",
        "six",
        "typeguard",
        "typing",
    ],
    include_package_data=True,
)
