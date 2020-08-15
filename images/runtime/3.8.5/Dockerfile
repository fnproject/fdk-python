FROM python:3.8.5-slim-buster

RUN apt-get update && apt-get upgrade -qy && apt-get clean
RUN addgroup --system --gid 1000 fn && adduser --system --uid 1000 --ingroup fn fn
