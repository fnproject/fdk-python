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

import ujson


def read_json(stream) -> dict:

    line = bytes()
    ret = False

    while True:
        c = stream.read(1)
        if c is None:
            continue
        if len(c) == 0:
            return ujson.loads(line)
        if c.decode() == "}":
            line += c
            ret = True
        elif c.decode() == "\n" and ret:
            line += c
            return ujson.loads(line)
        else:
            ret = False
            line += c
