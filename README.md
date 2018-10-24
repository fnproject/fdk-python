FN development kit for Python
=============================

Purpose of this library to provide simple interface to parse HTTP 1.1 requests represented as string

Following examples are showing how to use API of this library to work with streaming HTTP requests from Fn service.

Handling Hot JSON Functions
---------------------------

A main loop is supplied that can repeatedly call a user function with a series of HTTP requests.
In order to utilise this, you can write your `app.py` as follows:

```python
import fdk


def handler(context, data=None, loop=None):
    return data


if __name__ == "__main__":
    fdk.handle(handler)

```

Unittest your functions
--------------------------

Starting v0.0.33 FDK-Python provides a testing framework that allows performing unit tests of your function's code.
The unit test framework is the [pytest](https://pytest.org/). Coding style remain the same, so, write your tests as you've got used to.
Here's the example of the test suite:
```python
import fdk
import ujson

from fdk import fixtures


def handler(ctx, data=None, loop=None):
    name = "World"
    if data and len(data) > 0:
        body = ujson.loads(data)
        name = body.get("name")
    return {"message": "Hello {0}".format(name)}


async def test_parse_request_without_data(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, handler)

    content, status, headers = await call

    assert 200 == status
    assert {"message": "Hello World"} == ujson.loads(content)
    assert "application/json" in headers.get("Content-Type")


if __name__ == "__main__":
    fdk.handle(handler)

```

As you may see all assertions being performed with native assertion command.

In order to run tests, use the following command:
```bash
pytest -v -s --tb=long func.py
```

```bash
$ pytest -v -s --tb=long func.py
pytest -v -s --tb=long func.py
========================================================================================= test session starts ==========================================================================================
platform darwin -- Python 3.6.2, pytest-3.5.1, py-1.5.3, pluggy-0.6.0 -- /Users/denismakogon/Documents/oracle/go/src/github.com/fnproject/fdk-python/.venv/bin/python3.6
cachedir: .pytest_cache
rootdir: /Users/denismakogon/Documents/oracle/go/src/github.com/fnproject/test, inifile:
plugins: cov-2.4.0, aiohttp-0.3.0
collected 1 item                                                                                                                                                                                       

func.py::test_parse_request_without_data[pyloop] 2018-10-01 17:58:22,552 - asyncio - DEBUG - Using selector: KqueueSelector
2018-10-01 17:58:22,559 - aiohttp.access - INFO - 127.0.0.1 [01/Oct/2018:14:58:22 +0000] "POST /call HTTP/1.1" 200 188 "-" "Python/3.6 aiohttp/3.4.4"
PASSED

======================================================================================= 1 passed in 0.04 seconds =======================================================================================```

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
platform darwin -- Python 3.6.2, pytest-3.5.1, py-1.5.3, pluggy-0.6.0 -- /Users/denismakogon/Documents/oracle/go/src/github.com/fnproject/fdk-python/.venv/bin/python3.6
cachedir: .pytest_cache
rootdir: /Users/denismakogon/Documents/oracle/go/src/github.com/fnproject/test, inifile:
plugins: cov-2.4.0, aiohttp-0.3.0
collected 1 item                                                                                                                                                                                       

func.py::test_parse_request_without_data[pyloop] 2018-10-01 17:58:49,475 - asyncio - DEBUG - Using selector: KqueueSelector
2018-10-01 17:58:49,491 - aiohttp.access - INFO - 127.0.0.1 [01/Oct/2018:14:58:49 +0000] "POST /call HTTP/1.1" 200 188 "-" "Python/3.6 aiohttp/3.4.4"
PASSED

---------- coverage: platform darwin, python 3.6.2-final-0 -----------
Name      Stmts   Miss  Cover
-----------------------------
func.py      17      3    82%


======================================================================================= 1 passed in 0.08 seconds =======================================================================================
```



If you'd like to add more assertions to an upstream - please open an issue.


Applications powered by Fn: Concept
-----------------------------------

FDK is not only about developing functions, but providing necessary API to build serverless applications
that look like nothing but classes with methods powered by Fn.

```python
import requests
import ujson

from fdk.application import decorators


GPI_IMAGE = "denismakogon/python3-fn-gpi:0.0.6"


@decorators.fn_app
class Application(object):

    def __init__(self, *args, **kwargs):
        pass

    @decorators.fn(gpi_image=GPI_IMAGE)
    def dummy(*args, **kwargs) -> str:
        return ""

    @decorators.fn(gpi_image=GPI_IMAGE)
    def square(self, x: int, y: int, *args, **kwargs) -> bytes:
        return x * y

    @decorators.with_type_cast(
        return_type=lambda x: {"power": x})
    @decorators.fn(gpi_image=GPI_IMAGE)
    def power(self, x: int, y: int, *args, **kwargs) -> dict:
        return x ** y

    @decorators.with_type_cast(
        return_type=lambda x: ujson.loads(x))
    @decorators.fn(gpi_image=GPI_IMAGE, dependencies={
        "requests_get": requests.get
    })
    def request(self, *args, **kwargs) -> dict:
        requests_get = kwargs["dependencies"].get("requests_get")
        r = requests_get('https://api.github.com/events')
        r.raise_for_status()
        return r.content


if __name__ == "__main__":
    app = Application(config={"FDK_DEBUG": "1"})

    res, err = app.square(10, 20)
    if err:
        raise err
    print("square result type: ", type(res))
    print(res)

    res, err = app.power(10, 2)
    if err:
        raise err
    print("power result type: ", type(res))
    print(res)

    res, err = app.request()
    if err:
        raise err
    print("GitHub query result type: ", type(res))
    print(res)

    res, err = app.dummy()
    if err:
        raise err
    print("dummy result type: ", type(res))
    print(res if res else "<empty string>")

```
In order to identify to which Fn instance code needs to talk set following env var:

```bash
    export FN_API_URL = http://localhost:8080
```
with respect to IP address or domain name where Fn lives.

Applications powered by Fn: advanced serverless functions
---------------------------------------------------------

Since release v0.0.3 developer can consume new API to build truly serverless functions
without taking care of Docker images, application, etc.

```python
    @decorators.fn(gpi_image=GPI_IMAGE)
    def square(self, x: int, y: int, *args, **kwargs) -> bytes:
        return x * y

    @decorators.with_type_cast(
        return_type=lambda x: ujson.loads(x))
    @decorators.fn(gpi_image=GPI_IMAGE, dependencies={
        "requests_get": requests.get
    })
    def request(self, *args, **kwargs) -> dict:
        requests_get = kwargs["dependencies"].get("requests_get")
        r = requests_get('https://api.github.com/events')
        r.raise_for_status()
        return r.content
```

Each function decorated with `@decorator.fn` will become truly serverless and distributed.
So, how it works?

    * A developer writes function
    * FDK(Fn - powered app) creates a recursive Pickle v4.0 with 3rd - party dependencies
    * FDK(Fn - powered app) transfers pickled object to a function based on Python3 GPI(general purpose image)
    * FDK unpickles function and its 3rd - party dependencies and runs it
    * Function sends response back to Fn - powered application function caller

So, each CPU - intensive functions can be sent to Fn with the only load on networking(given example creates 7kB of traffic between app's host and Fn).


Applications powered by Fn: exceptions
--------------------------------------

Applications powered by Fn are following Go - like errors concept. It gives you full control on errors whether raise them or not.
```python
    res, err = app.square(10, 20)
    if err:
        raise err
    print(res)
```
Each error is an instance fn `FnError` that encapsulates certain logic that makes hides HTTP errors and turns them into regular Python - like exceptions.

