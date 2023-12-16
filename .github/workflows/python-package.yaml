name: Run Tests

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8

    - name: Checkout Repository
      uses: actions/checkout@v2

    - name: Install Python dependencies
      uses: py-actions/py-dependency-install@v4
      with:
        path: "requirements.txt"
        update-pip: "true"
        update-setuptools: "true"
        update-wheel: "true"

    - name: Run tests
      run: pytest tests
