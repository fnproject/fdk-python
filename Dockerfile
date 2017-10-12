FROM python:3.6.2


RUN mkdir /code
ADD . /code/
RUN pip install -e /code/

WORKDIR /code/samples/hot/json/echo
ENTRYPOINT ["python3", "func.py"]
