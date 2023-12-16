from setuptools import setup, find_packages

from logly.version import get_Version

VERSION = "0.0.0"

get_Version(VERSION)

DESCRIPTION = 'logly is a Python package for logging.'

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
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    license='MIT License',

)

print("Happy Coding!")
