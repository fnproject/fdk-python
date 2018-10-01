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
import fdk
import ujson

from fdk import log
from fdk import response


def handler(ctx, data=None, **kwargs):
    """
    General purpose Python3.7 function processor

    Why general purpose?

     - It supports any call from Fn-powered Python applications
       that utilizes corresponding API to run
       distributed Python functions

    How is it different from other Python FDK functions?

     - This function works with serialized Python callable objects via wire.
       Each function supplied with set of external dependencies that are
       represented as serialized functions, no matter if they are module-level,
       class-level Python objects

    :param ctx: request context
    :type ctx: fdk.context.RequestContext
    :param data: request data
    :type data: dict
    :return: resulting object of distributed function
    :rtype: object
    """
    log.log("income data type: {0}".format(type(data)))
    log.log("data len: {}".format(len(data)))
    payload = ujson.loads(data)
    (self_in_bytes,
     action_in_bytes, action_args, action_kwargs) = (
        payload['self'],
        payload['action'],
        payload['args'],
        payload['kwargs'])

    log.log("Got {} bytes of class instance".format(len(self_in_bytes)))
    log.log("Got {} bytes of function".format(len(action_in_bytes)))
    log.log("string class instance unpickling")

    self = dill.loads(bytes(self_in_bytes))

    log.log("class instance unpickled, type: {}".format(type(self)))
    log.log("string class instance function unpickling")

    action = dill.loads(bytes(action_in_bytes))

    log.log("class instance function unpickled, type: {}".format(type(action)))

    action_args.insert(0, self)

    dependencies = action_kwargs.get("dependencies", {})
    log.log("cached external methods found: {0}".format(len(dependencies) > 0))
    for name, method_in_bytes in dependencies.items():
        dependencies[name] = dill.loads(bytes(method_in_bytes))

    action_kwargs["dependencies"] = dependencies

    log.log("cached dependencies unpickled")

    try:
        res = action(*action_args, **action_kwargs)
    except Exception as ex:
        log.log("call failed")
        return response.RawResponse(
            ctx,
            status_code=500,
            response_data=str(ex))

    log.log("call result: {}".format(res))

    return response.RawResponse(
        ctx,
        status_code=200,
        response_data=res)


if __name__ == "__main__":
    fdk.handle(handler)
