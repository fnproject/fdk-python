# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

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
