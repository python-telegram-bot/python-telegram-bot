FROM python:3.10-slim-buster

RUN python -m pip install --upgrade pip
RUN pip install pipenv
WORKDIR /home
COPY bot .
RUN pipenv install -r requirements.txt
ENTRYPOINT [ "pipenv", "run", "python", "main.py" ] 
