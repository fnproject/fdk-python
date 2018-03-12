FROM python:3.6.2


RUN mkdir /code
ADD . /code/
RUN pip3 install -r /code/requirements.txt
RUN pip3 install -e /code/

WORKDIR /code/samples/echo
ENTRYPOINT ["python3", "func.py"]
