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

import os
import requests
import testtools

from fdk.application import decorators
from fdk.application import errors


@decorators.fn_app
class Application(object):

    def __init__(self, *args, **kwargs):
        pass

    @decorators.with_fn(fn_image="denismakogon/os.environ:latest")
    def env(self, fn_data=None):
        return fn_data

    @decorators.with_fn(fn_image="denismakogon/py-traceback-test:0.0.1",
                        fn_format="http")
    def traceback(self, fn_data=None):
        return fn_data

    @decorators.fn(fn_type="sync")
    def square(self, x, y, *args, **kwargs):
        return x * y

    @decorators.fn(fn_type="sync", dependencies={
        "requests_get": requests.get
    })
    def request(self, *args, **kwargs):
        requests_get = kwargs["dependencies"].get("requests_get")
        r = requests_get('https://api.github.com/events')
        r.raise_for_status()
        return r.text


class TestApplication(testtools.TestCase):

    @testtools.skipIf(os.getenv("API_URL") is None,
                      "API_URL is not set")
    def test_can_call_with_fn(self):
        app = Application(config={})
        res, err = app.env()
        self.assertIsNone(err, message=str(err))

    @testtools.skipIf(os.getenv("API_URL") is None,
                      "API_URL is not set")
    def test_can_get_traceback(self):
        app = Application(config={})
        res, err = app.traceback()
        self.assertIsNotNone(err, message=str(err))
        self.assertIsInstance(err, errors.FnError)

    # @testtools.skipIf(os.getenv("API_URL") is None,
    #                   "API_URL is not set")
    # def test_can_call_fn_simple(self):
    #     app = Application(config={})
    #     res, err = app.square(10, 20)
    #     self.assertIsNone(err, message=str(err))
    #     self.assertEqual(int(res), 10 * 20)
    #
    # @testtools.skipIf(os.getenv("API_URL") is None,
    #                   "API_URL is not set")
    # def test_can_call_fn_with_deps(self):
    #     app = Application(config={})
    #     res, err = app.request()
    #     self.assertIsNone(err, message=str(err))
    #     self.assertNotNone(res)


# NOTE: somehow dill pickler doesn't work fine in tests,
# it gives pretty weird error:
# _pickle.PicklingError: Can't pickle
# <class 'fdk.tests.test_application.Application'>:
# it's not the same object as fdk.tests.test_application.Application
#
# That why this module should be tested separately as CLI script
if __name__ == "__main__":
    if os.getenv("API_URL") is not None:
        app = Application(config={})

        res, err = app.square(10, 20)
        if err:
            raise err
        print(res)

        res, err = app.request()
        if err:
            raise err
        print(res)
    else:
        print("API_URL not test, skipping...")
