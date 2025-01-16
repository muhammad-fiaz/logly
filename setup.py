from setuptools import setup, find_packages

VERSION = "0.0.8"

DESCRIPTION = 'Logly: Ready to Go Python logging utility with color-coded messages, file-based logging, and many more customizable options. Simplify logging in your Python applications with Logly.'

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
        "logging", "custom-logging", "logly", "logging-utility", "python", "logs"
    ],
    classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Logging",
    ],
    python_requires='>=3.8',
    install_requires=[
        'pytest==8.3.4',
        'packaging==24.2',
        'colorama>=0.4.4',
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
