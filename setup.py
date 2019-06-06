from setuptools import setup, find_packages

# The text of the README file
README = open("README.md").read()

# This call to setup() does all the work
setup(
    name="codePost-api",
    version="1.0.11",
    description="Python bindings for the codePost API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/codepost-io/codePost-api-python",
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
    ],
    include_package_data=True,
)
