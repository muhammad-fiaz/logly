from setuptools import setup, find_packages

VERSION = "0.0.6"

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
        'log', 'logging', 'logly', 'python'
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
        'pytest==8.1.1',
        'packaging==24.0',
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
