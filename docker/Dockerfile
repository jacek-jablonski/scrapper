FROM python:3.7 as scrapper

ENV PROJECT_NAME scrapper
ENV PROJECT_PATH /opt/${PROJECT_NAME}
ENV PIPENV_VENV_IN_PROJECT 1

RUN mkdir -p ${PROJECT_PATH}

WORKDIR ${PROJECT_PATH}

RUN pip install pipenv==2018.11.26
COPY Pipfile Pipfile.lock ./
RUN pipenv install

COPY scrapper/ ${PROJECT_NAME}

EXPOSE 8080

CMD pipenv run python -m ${PROJECT_NAME}
