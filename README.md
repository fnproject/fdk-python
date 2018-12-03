# Function development kit for Python


Purpose of this library to provide simple interface to parse HTTP 1.1 requests represented as string

Following examples are showing how to use API of this library to work with streaming HTTP requests from Fn service.

## Handling Hot JSON Functions


A main loop is supplied that can repeatedly call a user function with a series of HTTP requests.
In order to utilise this, you can write your `app.py` as follows:

```python
import ujson


async def handle(ctx, data=None):
    body = {}
    raw_body  = await data.readall()
    if len(raw_body) > 0:
        body = ujson.loads(raw_body)
    name = body.get("name", "World")
    return ujson.dumps({"message": "Hello {0}".format(name)})

```

## Unittest your functions


Starting v0.0.33 FDK-Python provides a testing framework that allows performing unit tests of your function's code.
The unit test framework is the [pytest](https://pytest.org/). Coding style remain the same, so, write your tests as you've got used to.
Here's the example of the test suite:
```python
import pytest
import ujson

from fdk import fixtures


def handler(ctx, data=None):
    name = "World"
    if data and len(data) > 0:
        body = ujson.loads(data)
        name = body.get("name")
    return {"message": "Hello {0}".format(name)}


@pytest.mark.asyncio
async def test_parse_request_without_data():
    call = fixtures.process_response(
        fixtures.setup_fn_call(
            handler,
        )
    )

    content, status, headers = await call

    assert "message" in content
    assert "Hello World" == content["message"]
    assert "application/json" in headers.get("Content-Type")

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
