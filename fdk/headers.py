#
# Copyright (c) 2019, 2020 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from fdk import constants


def decap_headers(hdsr, merge=True):
    ctx_headers = {}
    if hdsr is not None:
        for k, v in hdsr.items():
            k = k.lower()
            if k.startswith(constants.FN_HTTP_PREFIX):
                push_header(ctx_headers, k[len(constants.FN_HTTP_PREFIX):], v)
            elif merge:
                # http headers override functions headers in context
                # this is not ideal but it's the more correct view from the
                # consumer perspective than random choice and for things
                # like host headers
                if k not in ctx_headers:
                    ctx_headers[k] = v
    return ctx_headers


def push_header(input_map, key, value):
    if key not in input_map:
        input_map[key] = value
        return

    current_val = input_map[key]

    if isinstance(current_val, list):
        if isinstance(value, list):  # both lists concat
            input_map[key] = current_val + value
        else:  # copy and append current value
            new_val = current_val.copy()
            new_val.append(value)
            input_map[key] = new_val
    else:
        if isinstance(value, list):  # copy new list value and prepend current
            new_value = value.copy()
            new_value.insert(0, current_val)
            input_map[key] = new_value
        else:  # both non-lists create a new list
            input_map[key] = [current_val, value]


def encap_headers(headers, status=None):
    new_headers = {}
    if headers is not None:
        for k, v in headers.items():
            k = k.lower()
            if k.startswith(constants.FN_HTTP_PREFIX):  # by default merge
                push_header(new_headers, k, v)
            if (k == constants.CONTENT_TYPE
                    or k == constants.FN_FDK_VERSION):  # but don't merge these
                new_headers[k] = v
            else:
                push_header(new_headers, constants.FN_HTTP_PREFIX + k, v)

    if status is not None:
        new_headers[constants.FN_HTTP_STATUS] = str(status)

    return new_headers
