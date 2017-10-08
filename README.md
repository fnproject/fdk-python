FN development kit for Python
=============================

Purpose of this library to provide simple interface to parse HTTP 1.1 requests represented as string

Following examples are showing how to use API of this library to work with streaming HTTP requests from Fn service.

Handling Hot Functions
----------------------

A main loop is supplied that can repeatedly call a user function with a series of HTTP requests.
In order to utilise this, you can write your `app.py` as follows:

```python
import fdk

from fdk.http import response


def handler(context, **kwargs):
    body = kwargs.get('data')
    return response.RawResponse(context.version, 200, "OK", body.readall())


if __name__ == "__main__":
    fdk.handle(handler)

```

Automatic input coercions
-------------------------

Decorators are provided that will attempt to coerce input values to Python types.
Some attempt is made to coerce return values from these functions also:

```python
import fdk

@fdk.coerce_input_to_content_type
def handler(context, **kwargs):
    """
    body is a request body, it's type depends on content type
    """
    return kwargs.get('data')


if __name__ == "__main__":
    fdk.handle(handler)

```

Working with async automatic input coercions
--------------------------------------------

Latest version (from 0.0.6) supports async coroutines as a request body processors:
```python
import asyncio
import fdk

from fdk.http import response


@fdk.coerce_input_to_content_type
async def handler(context, **kwargs):
    headers = {
        "Content-Type": "plain/text",
    }
    return response.RawResponse(
        context.version, 200, "OK",
        http_headers=headers,
        response_data="OK")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    fdk.handle(handler, loop=loop)

```
As you can see `app` function is no longer callable, because its type: coroutine, so we need to bypass event loop inside 
