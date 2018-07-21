FROM python:3.6

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
ENV NAME leche

EXPOSE 5555
CMD ["python", "/code/runserver.py"]