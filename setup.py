import os
from setuptools import setup, find_packages

# The text of the README file
README = open("README.md").read()

# Get the version number without importing our package
# (which would trigger some ImportError due to missing dependencies)

version_contents = {}
with open(os.path.join("codepost", "version.py")) as f:
    exec(f.read(), version_contents)

# This call to setup() does all the work
setup(
    name="codepost",
    version=version_contents["__version__"],
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
        "blessings",
        "colorama",
        "eliot",
        "python_forge;python_version>'3.5'",
        "six",
        "typing",
        "enum34;python_version<'3.4'"
    ],
    include_package_data=True,
)
