FN development kit for Python
=============================

Purpose of this library to provide simple interface to parse HTTP 1.1 requests represented as string

Following examples are showing how to use API of this library to work with streaming HTTP requests from Fn service.

Handling Hot HTTP Functions
---------------------------

A main loop is supplied that can repeatedly call a user function with a series of HTTP requests.
In order to utilise this, you can write your `app.py` as follows:

```python
import fdk

from fdk.http import response


def handler(context, data=None, loop=None):
    return response.RawResponse(
        http_proto_version=context.version,
        status_code=200, 
        headers={}, 
        response_data=data.readall()
    )


if __name__ == "__main__":
    fdk.handle(handler)

```

Automatic HTTP input coercions
------------------------------

Decorators are provided that will attempt to coerce input values to Python types.
Some attempt is made to coerce return values from these functions also:

```python
import fdk

@fdk.coerce_http_input_to_content_type
def handler(context, data=None, loop=None):
    """
    body is a request body, it's type depends on content type
    """
    return data


if __name__ == "__main__":
    fdk.handle(handler)

```

Working with async automatic HTTP input coercions
-------------------------------------------------

Latest version supports async coroutines as a request body processors:
```python
import asyncio
import fdk

from fdk.http import response


@fdk.coerce_http_input_to_content_type
async def handler(context, data=None, loop=None):
    headers = {
        "Content-Type": "text/plain",
    }
    return response.RawResponse(
        http_proto_version=context.version,
        status_code=200,
        headers=headers,
        response_data="OK"
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    fdk.handle(handler, loop=loop)

```
As you can see `app` function is no longer callable, because its type: coroutine, so we need to bypass event loop inside 

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

Working with async Hot JSON Functions
-------------------------------------

Latest version supports async coroutines as a request body processors:
```python
import asyncio

import fdk


async def handler(context, data=None, loop=None):
    return data


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    fdk.handle(handler, loop=loop)

```

Applications powered by Fn: Concept
-----------------------------------

FDK is not only about developing functions, but providing necessary API to build serverless applications 
that look like nothing but classes with methods powered by Fn.

```python
from fdk.application import decorators


@decorators.fn_app
class Application(object):

    def __init__(self, *args, **kwargs):
        pass

    @decorators.fn_route(fn_image="denismakogon/os.environ:latest")
    def env(self, fn_data=None):
        return fn_data

    @decorators.fn_route(fn_image="denismakogon/py-traceback-test:0.0.1",
                         fn_format="http")
    def traceback(self, fn_data=None):
        return fn_data

if __name__ == "__main__":
    app = Application(config={})

    res, err = app.env()
    if err:
        raise err
    print(res)

    res, err = app.traceback()
    if err:
        raise err
    print(res)

```
In order to identify to which Fn instance code needs to talk set following env var:

```bash
    export API_URL=http://localhost:8080
```
with respect to IP address or domain name where Fn lives.


Applications powered by Fn: supply data to a function
-----------------------------------------------------

At this moment those helper-decorators let developers interact with Fn-powered functions as with regular class methods.
In order to pass necessary data into a function developer just needs to do following
```python

if __name__ == "__main__":
    app = Application(config={})

    app.env(keyone="blah", keytwo="blah", somethingelse=3)

```
Key-value args will be turned into JSON instance and will be sent to a function as payload body.


Applications powered by Fn: working with function's result
----------------------------------------------------------

In order to work with result from function you just need to read key-value argument `fn_data`:
```python
    @decorators.fn_route(fn_image="denismakogon/py-traceback-test:0.0.1",
                         fn_format="http")
    def traceback(self, fn_data=None):
        return fn_data
```

Applications powered by Fn: exceptions
--------------------------------------

Applications powered by Fn are following Go-like errors concept. It gives you full control on errors whether raise them or not.
```python
    res, err = app.env()
    if err:
        raise err
    print(res)

```
Each error is an instance fn `FnError` that encapsulates certain logic that makes hides HTTP errors and turns them into regular Python-like exceptions.

TODOs
-----

 - generic response class
 - use fdk.headers.GoLikeHeaders in http
