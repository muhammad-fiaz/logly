from setuptools import setup, find_packages

from logly.version import get_Version

VERSION = "0.0.1"

get_Version(VERSION)

DESCRIPTION = ('Logly: Python logging utility with color-coded messages and file support. Easily log and trace '
               'messages with customizable colors. Simple integration for effective debugging and monitoring.')

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="logly",
    version=VERSION,
    author="Muhammad Fiaz",
    author_email="contact@muhammmadfiaz.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/muhammad-fiaz/logly.git',
    packages=find_packages(),
    keywords=[
      'log'
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.8',
    install_requires=[
        'setuptools==69.0.2',
        'pytest==7.4.3',
        'packaging==23.2',
        'colorama==0.4.6',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    license='MIT License',
    project_urls={
        'Source Code': 'https://github.com/muhammad-fiaz/logly.git',
        'Bug Tracker': 'https://github.com/muhammad-fiaz/logly/issues',
        'Documentation': 'https://github.com/muhammad-fiaz/logly#readme',
    },
)

print("Happy Coding!")
