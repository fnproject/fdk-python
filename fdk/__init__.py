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

from fdk.http import handle as http_handler
from fdk.json import handle as json_handler


handle_http = http_handler.run
handle_json = json_handler.run
coerce_http_input_to_content_type = http_handler.coerce_input_to_content_type


def handle(handler, loop=None):
    """
    Generic format handler based on FN_FORMAT
    
    :param handler: a function or coroutine
    :param loop: asyncio event loop
    :type loop: asyncio.AbstractEventLoop
    :return: None
    """
    fn_format = os.environ.get("FN_FORMAT")
    if fn_format == "json":
        handle_json(handler, loop=loop)
    elif fn_format == "http":
        handle_http(handler, loop=loop)
    else:
        raise Exception("Unknown hot format")
