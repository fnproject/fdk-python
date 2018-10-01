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

import dill
import functools
import os
import requests

from fdk import constants
from fdk.application import errors


TRIGGER_ATTR = "__trigger_created"


def get_app_id_by_name(app_name, fn_api_url):
    list_apps = "{0}/v2/apps".format(fn_api_url)
    resp = requests.get(list_apps)
    resp.raise_for_status()
    apps = resp.json().get("items", [])
    for app_dct in apps:
        if app_dct["name"] == app_name:
            return app_dct["id"]
    return


def fn_app(fn_app_class):
    """
    Sets up Fn app with config

    @fn_app
    class MyApp(object):

        def __init__(self, *args, **kwargs):
            pass

        @fn_route(
            fn_image="<your-image>",
            fn_memory=256,
            fn_timeout=60,
            fn_idle_timeout=200,
        )
        def do_stuff(self, *args, fn_data=None, **kwargs):
            pass

    :param fn_app_class: any class
    :return: class decorator
    """
    @functools.wraps(fn_app_class)
    def wrapper(*args, **kwargs):
        app_name = fn_app_class.__name__.lower()
        fn_api_url = os.environ.get("FN_API_URL")
        requests.get(fn_api_url).raise_for_status()

        app_id = get_app_id_by_name(app_name, fn_api_url)
        if app_id is None:
            resp = requests.post(
                "{}/v2/apps".format(fn_api_url),
                json={
                    "name": app_name.lower(),
                    "config": kwargs.get("config"),
                    "syslog_url": kwargs.get("syslog_url"),
                }
            )
            resp.raise_for_status()
        return fn_app_class(*args)

    return wrapper


def fn(gpi_image=None, fn_timeout=60,
       fn_idle_timeout=200, fn_memory=256,
       dependencies=None):
    """
    Runs Python's function on general purpose Fn function


    What it does?

     Decorator does following:
       - collects dat for Fn route and creates it
       - when function called, that function transforms
         into byte array (Pickle) then gets sent to general
         purpose Fn Python3 function
       - each external dependency (3rd-party libs)
         that are required for func gets transformed
         into byte array (Pickle)

     It means that functions does't run locally but on Fn.

    How is it different from other Python FDK functions?

     - This function works with serialized Python callable objects via wire.
       Each function supplied with set of external dependencies that are
       represented as serialized functions, no matter if they are module-level,
       class-level Python objects

    :param fn_timeout: Fn function call timeout
    :type fn_timeout: int
    :param fn_idle_timeout: Fn function call idle timeout
    :type fn_idle_timeout: int
    :param fn_memory: Fn function memory limit
    :type fn_memory: int
    :param dependencies: Python's function 3rd-party callable dependencies
    :type dependencies: dict
    :return:
    """
    dependencies = dependencies if dependencies else {}

    def ext_wrapper(action):
        @functools.wraps(action)
        def inner_wrapper(*f_args, **f_kwargs):
            fn_api_url = os.environ.get("FN_API_URL")
            requests.get(fn_api_url).raise_for_status()
            self = f_args[0]
            fn_path = action.__name__.lower()
            app_name = self.__class__.__name__.lower()
            app_id = get_app_id_by_name(app_name, fn_api_url)
            if not hasattr(action, TRIGGER_ATTR):
                try:
                    # create a function
                    fn_id = None
                    resp = requests.post(
                        "{0}/v2/fns".format(fn_api_url), json={
                            "name": fn_path,
                            "app_id": app_id,
                            "image": gpi_image,
                            "memory": fn_memory if fn_memory else 256,
                            "format": constants.HTTPSTREAM,
                            "timeout": fn_timeout if fn_timeout else 60,
                            "idle_timeout": (fn_idle_timeout if
                                             fn_idle_timeout else 120),
                        }
                    )
                    if resp.status_code == 409:
                        # look for fn_id using fn name and app ID
                        fns_resp = requests.get(
                            "{0}/v2/fns?app_id={1}".format(fn_api_url, app_id))
                        fns_resp.raise_for_status()

                        fns = fns_resp.json().get("items", [])
                        for fn_dct in fns:
                            if fn_path == fn_dct.get("name"):
                                fn_id = fn_dct.get("id")

                    if resp.status_code != 200 and resp.status_code != 409:
                        resp.raise_for_status()
                    if resp.status_code == 200:
                        fn_id = resp.json().get("id")

                    # create a trigger
                    resp = requests.post(
                        "{0}/v2/triggers".format(fn_api_url), json={
                            "app_id": app_id,
                            "fn_id": fn_id,
                            "type": "http",
                            "name": "{}-trigger".format(fn_path),
                            "source": "/{}".format(fn_path),
                        }
                    )
                    if resp.status_code != 200 and resp.status_code != 409:
                        resp.raise_for_status()
                except requests.HTTPError as ex:
                    return None, Exception(ex.response.text)

                setattr(action, TRIGGER_ATTR, True)

            fn_trigger_url = "{}/t/{}/{}".format(
                fn_api_url, app_name, fn_path)

            # fn_trigger_url = "{}/invoke/{}".format(fn_api_url, fn_id)

            action_in_bytes = dill.dumps(action, recurse=True)
            self_in_bytes = dill.dumps(self, recurse=True)

            for name, method in dependencies.items():
                dependencies[name] = list(dill.dumps(method, recurse=True))

            f_kwargs.update(dependencies=dependencies)
            try:

                resp = requests.post(fn_trigger_url, json={
                    "action": list(action_in_bytes),
                    "self": list(self_in_bytes),
                    "args": f_args[1:],
                    "kwargs": f_kwargs,
                })
                resp.raise_for_status()
            except requests.HTTPError as ex:
                ex.response.close()
                return None, errors.FnError(
                    "{}/{}".format(app_name, fn_path),
                    ex.response.content)

            content_len = int(resp.headers.get("Content-Length", 0))
            return resp.json() if content_len > 0 else resp.text, None

        return inner_wrapper

    return ext_wrapper


def with_type_cast(return_type=lambda x: x):
    """
    Casts the response body to a different type.

    @decorators.with_type_cast(
    return_type=lambda x: {"square": int(x.decode("utf8"))})
    @decorators.fn(fn_type="sync")
    def square(self, x: int, y: int, *args, **kwargs) -> int:
        return x * y

    This decorator accepts the callable object as a parameter
    to apply that to the function's response data for type casting.
    The default response type from the function is - bytes.

    :param return_type: a callable object for processing the result
    :type return_type: types.FunctionType
    :return: type-casted function response data
    """

    def ext_wrapper(action):
        @functools.wraps(action)
        def inner_wrapper(*args, **kwargs):
            result, err = action(*args, **kwargs)
            if err is not None:
                return None, err

            return return_type(result), None

        return inner_wrapper

    return ext_wrapper
