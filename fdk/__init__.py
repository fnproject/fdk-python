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

import asyncio
import uvloop

from fdk import runner


def handle(handle_func, loop=None):
    with open("/dev/stdin", "rb", buffering=0) as stdin:
        if loop is None:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            loop = asyncio.get_event_loop()
        try:
            cls = runner.JSONProtocol.with_handler(handle_func, loop=loop)
            stdin_pipe_reader = loop.connect_read_pipe(cls, stdin)
            loop.run_until_complete(stdin_pipe_reader)
            loop.run_forever()
        finally:
            loop.close()
