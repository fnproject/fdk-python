ARG PY_VERSION=latest
FROM fnproject/python:${PY_VERSION}-dev as build-stage
ARG PKG_VERSION="1.0.0_SNAPSHOT"
ARG PKG_EXTENSION="-py3-none-any.whl"
COPY . /function
WORKDIR /function
            RUN pip3 install --target /python/  --no-cache --no-cache-dir fdk-${PKG_VERSION}${PKG_EXTENSION} &&\
            pip3 install --target /python/  --no-cache --no-cache-dir -r requirements.txt &&\
            rm -fr ~/.cache/pip /tmp* fdk-${PKG_VERSION}${PKG_EXTENSION} requirements.txt func.yaml Dockerfile .venv &&\
            chmod -R o+r /python
RUN rm -fr /function/.pip_cache
FROM fnproject/python:${PY_VERSION}
WORKDIR /function
COPY --from=build-stage /python /python
COPY --from=build-stage /function /function
RUN chmod -R o+r /function
ENV PYTHONPATH=/function:/python
ENTRYPOINT ["/python/bin/fdk", "/function/func.py", "handler"]