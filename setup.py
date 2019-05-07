from setuptools import setup, find_packages
from codecs import open
from os import path

from expandvars import __author__
from expandvars import __description__
from expandvars import __email__
from expandvars import __license__
from expandvars import __homepage__
from expandvars import __license__
from expandvars import __version__


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="expandvars",
    version=__version__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__homepage__,
    author=__author__,
    author_email=__email__,
    license=__license__,
    py_modules=["expandpath"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
        "Topic :: Software Development",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft",
    ],
    platforms=["Any"],
    keywords="expand system variables",
    packages=find_packages(exclude=["contrib", "docs", "tests", "examples"]),
    install_requires=[],
    extras_require={"testing": ["pytest>=4.4.1", 'pytest-cov>=2.7.1']},
)
