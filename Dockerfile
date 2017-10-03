FROM python:3.6.2


RUN mkdir /code
ADD . /code/
RUN pip install -e /code/

WORKDIR /code/samples/hot
ENTRYPOINT ["python3", "app.py"]
