FROM python:3.6

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
ARG ENV_MODE
ENV FLASK_ENV ${ENV_MODE}

EXPOSE 5000
CMD ["python", "/code/runserver.py"]