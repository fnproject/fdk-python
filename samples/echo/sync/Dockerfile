FROM python:3.7

RUN mkdir /code
ADD ./ /code/
WORKDIR /code/
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "func.py"]
