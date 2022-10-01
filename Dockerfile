# base python
FROM python:3.10-slim

# working directory for the api
WORKDIR /home/auth

## the code
COPY main.py main.py
COPY api api

# database with 1 admin user
COPY user.db user.db

# testing code
COPY test test

# virtual environment
RUN python -m venv .env 
# package requirements
COPY requirements.txt requirements.txt
RUN .env/bin/pip install -r requirements.txt

# run the testing
RUN .env/bin/pytest -v --cov=api/ --cov-report=term-missing test/

# start the auth server
CMD [".env/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]