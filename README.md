# Function development kit for Python
The python FDK lets you write functions in python 3.6/3.7/3.8

## Simplest possible function 
 
```python
import io
import logging

from fdk import response

def handler(ctx, data: io.BytesIO = None):
    logging.getLogger().info("Got incoming request")
    return response.Response(ctx, response_data="hello world")
```


## Handling HTTP metadata in HTTP Functions 
Functions can implement HTTP services when fronted by an HTTP Gateway

When your function is behind an HTTP gateway you can access the inbound HTTP Request via :

  - `ctx.HttpHeaders()` : a map of string -> value | list of values , unlike `ctx.Headers()` this only includes headers 
        passed by the HTTP gateway (with no functions metadata).
  - `ctx.RequestURL()` : the incoming request URL passed by the gateway 
  - `ctx.Method()` : the HTTP method of the incoming request 
   
You can set outbound HTTP headers and the HTTP status of the request using `ctx.SetResponseHeaders` or the `Response`    
  - e.g. `ctx.SetResponseHeaders({"Location","http://example.com/","My-Header2": ["v1","v2"]}, 302)` 
  - or by passing these to the Response object : 
```python
return new Response(
    ctx,
    headers={"Location","http://example.com/","My-Header2": ["v1","v2"]},
    response_data="Page moved",
    status_code=302)
```

e.g. to redirect users to a different page : 
```python
import io
import logging

from fdk import response

def handler(ctx, data: io.BytesIO = None):
    logging.getLogger().info("Got incoming request for URL %s with headers %s", ctx.RequestURL(), ctx.HTTPHeaders())
    ctx.SetResponseHeaders({"Location": "http://www.example.com"}, 302)
    return response.Response(ctx, response_data="Page moved from %s")
```


## Handling JSON in  Functions

A main loop is supplied that can repeatedly call a user function with a series of requests.
In order to utilise this, you can write your `func.py` as follows:

```python
import json
import io

from fdk import response

def handler(ctx, data: io.BytesIO=None):
    name = "World"
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        print(str(ex))
        pass

    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "Hello {0}".format(name)}),
        headers={"Content-Type": "application/json"}
    )

```

## Writing binary data from functions 
In order to write a binary response to your function pass a `bytes` object to the response_data

```python
import io 
from PIL import Image, ImageDraw 
from fdk import response 
 
 
def handler(ctx, data: io.BytesIO=None): 
    img = Image.new('RGB', (100, 30), color='red') 
    d = ImageDraw.Draw(img) 
    d.text((10, 10), "hello world", fill=(255, 255, 0)) 
    # write png image to memory  
    output =  io.BytesIO() 
    img.save(output, format="PNG") 
    # get the bytes of the image  
    imgbytes = output.getvalue() 
 
    return response.Response( 
        ctx, response_data=imgbytes, 
        headers={"Content-Type": "image/png"} 
    )
```



## Unit testing your functions

Starting v0.0.33 FDK-Python provides a testing framework that allows performing unit tests of your function's code.
The unit test framework is the [pytest](https://pytest.org/). Coding style remain the same, so, write your tests as you've got used to.
Here's the example of the test suite:
```python
import json
import io
import pytest

from fdk import fixtures
from fdk import response


def handler(ctx, data: io.BytesIO=None):
    name = "World"
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        print(str(ex))
        pass

    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "Hello {0}".format(name)}),
        headers={"Content-Type": "application/json"}
    )


@pytest.mark.asyncio
async def test_parse_request_without_data():
    call = await fixtures.setup_fn_call(handler)

    content, status, headers = await call

    assert 200 == status
    assert {"message": "Hello World"} == json.loads(content)

```

As you may see all assertions being performed with native assertion command.

In order to run tests, use the following command:
```bash
pytest -v -s --tb=long func.py
```

```bash
========================================================================================= test session starts ==========================================================================================
platform darwin -- Python 3.7.1, pytest-4.0.1, py-1.7.0, pluggy-0.8.0 -- /python/bin/python3
cachedir: .pytest_cache
rootdir: /Users/denismakogon/go/src/github.com/fnproject/test, inifile:
plugins: cov-2.4.0, asyncio-0.9.0, aiohttp-0.3.0
collected 1 item                                                                                                                                                                                       

func.py::test_parse_request_without_data 2018-12-10 15:42:30,029 - asyncio - DEBUG - Using selector: KqueueSelector
2018-12-10 15:42:30,029 - asyncio - DEBUG - Using selector: KqueueSelector
'NoneType' object has no attribute 'getvalue'
{'Fn-Http-Status': '200', 'Content-Type': 'application/json'}
PASSED

======================================================================================= 1 passed in 0.02 seconds =======================================================================================
```

To add coverage first install one more package:
```bash
pip install pytest-cov
```
then run tests with coverage flag:
```bash
pytest -v -s --tb=long --cov=func func.py
```

```bash
pytest -v -s --tb=long --cov=func func.py
========================================================================================= test session starts ==========================================================================================
platform darwin -- Python 3.7.1, pytest-4.0.1, py-1.7.0, pluggy-0.8.0 -- /python/bin/python3
cachedir: .pytest_cache
rootdir: /Users/denismakogon/go/src/github.com/fnproject/test, inifile:
plugins: cov-2.4.0, asyncio-0.9.0, aiohttp-0.3.0
collected 1 item                                                                                                                                                                                       

func.py::test_parse_request_without_data 2018-12-10 15:43:10,339 - asyncio - DEBUG - Using selector: KqueueSelector
2018-12-10 15:43:10,339 - asyncio - DEBUG - Using selector: KqueueSelector
'NoneType' object has no attribute 'getvalue'
{'Fn-Http-Status': '200', 'Content-Type': 'application/json'}
PASSED

---------- coverage: platform darwin, python 3.7.1-final-0 -----------
Name      Stmts   Miss  Cover
-----------------------------
func.py      19      1    95%


======================================================================================= 1 passed in 0.06 seconds =======================================================================================
```

## FDK tooling

## Installing tools

Create a virtualenv:
```bash
python3 -m venv .venv
```
Activate virtualenv:
```bash
source .venv/bin/activate
```
All you have to do is:
```bash
pip install fdk
```
Now you have a new tools added!

## Tools

With a new FDK release a new set of tooling introduced:

 - `fdk` - CLI tool, an entry point to a function, that's the way you start your function in real life
 - `fdk-tcp-debug` - CLI tool, an entry point to a function local debugging

## CLI tool: `fdk`

This is an entry point to a function, this tool you'd be using while working with a function that is deployed at Fn server.

### Usage

`fdk` is a Python CLI script that has the following signature:

```bash
fdk <path-to-a-function-module> [module-entrypoint]
```

where:
    - `fdk` is a CLI script
    - `<path-to-a-function-module>` is a path to your function's code, for instance, `/function/func.py`
    - `[module-entrypoint]` is an entry point to a module, basically you need to point to a method that has the following signature:
    `def <function_name>(ctx, data: io.BytesIO=None)`, as you many notice this is a ordinary signature of Python's function you've used to while working with an FDK,

The parameter `[module-entrypoint]` has a default value: `handler`. It means that if a developer will point an `fdk` CLI to a module `func.py`:

```
fdk func.py
```

the CLI will look for `handler` Python function.
In order to override `[module-entrypoint]` you need to specify your custom entry point.

### Testing locally

To run a function locally (outside Docker) you need to set `FN_FORMAT` and `FN_LISTENER`, like so:

```bash
env FDK_DEBUG=1 FN_FORMAT=http-stream FN_LISTENER=unix://tmp/func.sock fdk <path-to-a-function-module> [module-entrypoint]
```

You can then test with curl:

```bash
curl -v --unix-socket /tmp/func.sock -H "Fn-Call-Id: 0000000000000000" -H "Fn-Deadline: 2030-01-01T00:00:00.000Z" -XPOST http://function/call -d '{"name":"Tubbs"}'
```

## CLI tool: `fdk-tcp-debug`

The reason why this tool exists is to give a chance to developers to debug their function on their machines.
There's no difference between this tool and `fdk` CLI tool, except one thing: `fdk` works on top of the unix socket,
when this tool works on top of TCP socket, so, the difference is a transport, nothing else.

#### Usage

`fdk-tcp-debug` is a Python CLI script that has the following signature:

```bash
fdk-tcp-debug <port> <path-to-a-function-module> [module-entrypoint]
```

The behaviour of this CLI is the same, but it will start an FDK on top of the TCP socket.
The only one difference is that this CLI excepts one more parameter: `port` that is required by TCP socket configuration.

Now you can test your functions not only with the unit tests but also see how it works within the FDK before actually deploying them to Fn server.


## Developing and testing an FDK

If you decided to develop an FDK please do the following:

 - open an issue with the detailed description of your problem
 - checkout a new branch with the following signature: `git checkout -b issue-<number>`

In order to test an FDK changes do the following:

 - `python3 -m venv .venv && source .venv/bin/activate`
 - `pip install tox`
 - `tox`
 
### Testing with `fdk-tcp-debug`

Test an FDK change with sample function using `fdk-tcp-debug`:

```bash
pip install -e .
FDK_DEBUG=1 fdk-tcp-debug 5001 samples/echo/func.py handler
```

Then just do:

```bash
curl -v -X POST localhost:5001 -d '{"name":"denis"}'
```

### Testing within a function

First of all create a test function:
```bash
fn init --runtime python3.8 test-function
```

Create a Dockerfile in a function's folder:
```dockerfile
FROM fnproject/python:3.8-dev as build-stage

ADD . /function
WORKDIR /function

RUN pip3 install --target /python/  --no-cache --no-cache-dir fdk-test-py3-none-any.whl 

RUN rm -fr ~/.cache/pip /tmp* requirements.txt func.yaml Dockerfile .venv

FROM fnproject/python:3.8

COPY --from=build-stage /function /function
COPY --from=build-stage /python /python
ENV PYTHONPATH=/python

ENTRYPOINT ["/python/bin/fdk", "/function/func.py", "handler"]
```

Build an FDK wheel:
```bash
pip install wheel
PBR_VERSION=test python setup.py bdist_wheel
```

Move an FDK wheel (located at `dist/fdk-test-py3-none-any.whl`) into a function's folder.

Do the deploy:
```bash
fn --versbose deploy --app testapp --local --no-bump
fn config fn testapp test-function FDK_DEBUG 1
```

And the last step - invoke it and see how it goes:
```bash
fn invoke testapp test-function
```

## Speeding up an FDK

FDK is based on the asyncio event loop. Default event loop is not quite fast, but works on all operating systems (including Windows),
In order to make an FDK to process IO operation at least 4 times faster you need to add another dependency to your function:

```text
uvloop
```

[UVLoop](https://github.com/MagicStack/uvloop) is a CPython wrapper on top of cross-platform [libuv](https://github.com/libuv/libuv).
Unfortunately, uvloop doesn't support Windows for some reason, so, in order to let developers test their code on Windows
FDK doesn't install uvloop by default, but still has some checks to see whether it is installed or not.


## Migration path

As if you are the one who used Python FDK before and would like to update - please read this section carefully.
A new FDK is here which means there suppose to be a way to upgrade your code from an old-style FDK to a new-style FDK.

### No `__main__` definition

As you noticed - an entry point a function changed, i.e., func.py no longer considered as the main module (`__main__`) which means that the following section:

```python
if __name__ == "__main__":
    fdk.handle(handler)
```

has no effect any longer. Please note that FDK will fail-fast with an appropriate message if old-style FDK format used.

### `data` type has changed

With a new FDK, `data` parameter is changing from `str` to `io.BytesIO`.
The simplest way to migrate is to wrap your data processing code with 1 line of code:
```python
data = data.read()
```

If you've been using json lib to turn an incoming data into a dictionary you need to replace: `json.loads` with `json.load`

```python
try:
    dct = json.load(data)
except ValueError as ex:
    # do here whatever is reasonable
```

### Dockerfile
If you've been using CLI to build function without modifying runtime in `func.yaml` to `docker` 
instead of `python` then the only thing you need is to update the CLI to the latest version and 
pin your Python runtime version to `python`, `python3.7`, or `python3.8`.

If you've been using custom multi-stage Dockerfile (derived from what Fn CLI generates) 
the only thing that is necessary to change is an `ENTRYPOINT` from:

```text
ENTRYPOINT["python", "func.py"]
```

to:

```text
ENTRYPOINT["/python/bin/fdk", "func.py", "handler"]
```

If you've been using your own Dockerfile that wasn't derived from the Dockerfile 
that CLI is generating, then you need to search in your `$PATH` where CLI fdk was installed 
(on Linux, it will be installed to `/usr/local/bin/fdk`). At most of the times, if you've been using:

```text
pip install --target <location> ...
```

then you need to search fdk CLI at `<location>/bin/fdk`, this is what Fn CLI does by calling the following command:

```text
pip install --target /python ...
```

## Notes

A new FDK will abort a function execution if old-style function definition is used.
Make sure you check you migrated your code wisely.
