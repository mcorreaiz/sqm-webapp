FROM python:3.6

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
ARG ENV_MODE
ENV DEPLOY_MODE ${ENV_MODE}

EXPOSE 5555
CMD ["python", "/code/runserver.py"]