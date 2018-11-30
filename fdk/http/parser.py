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


async def readline(stream):
    """Read a line up until the \r\n termination
    Return the line with that terminator included"""
    l = bytes()
    ret = False

    while True:
        c = await stream.read(1)
        if c is None:
            continue
        if len(c) == 0:
            return l.decode('ascii')
        elif c == b'\r':
            l += c
            ret = True
        elif c == b'\n' and ret:
            l += c
            return l.decode('ascii')
        else:
            ret = False
            l += c
