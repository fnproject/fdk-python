# Function development kit for Python


While the FDK contract is HTTP, the intention is for that to be somewhat 
abstracted from the user - they write some Function code , this library helps them do that.

## Handling JSON Functions


A main loop is supplied that can repeatedly call a user function with a series of requests.
In order to utilise this, you can write your `func.py` as follows:

```python
import io
import json


async def handler(ctx, data: io.BytesIO=None):
    name = "World"
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        print(str(ex))

    return {"message": "Hello {0}".format(name)}

```

## Unittest your functions


Starting v0.0.33 FDK-Python provides a testing framework that allows performing unit tests of your function's code.
The unit test framework is the [pytest](https://pytest.org/). Coding style remain the same, so, write your tests as you've got used to.
Here's the example of the test suite:
```python
import json
import pytest

from fdk import fixtures


async def handler(ctx, data=None):
    name = "World"
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        print(str(ex))

    return {"message": "Hello {0}".format(name)}


@pytest.mark.asyncio
async def test_parse_request_without_data():
    call = await fixtures.setup_fn_call(handler)

    content, status, headers = await call

    assert 200 == status
    assert {"message": "Hello World"} == content

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
