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

from fdk import constants


def decap_headers(hdsr):
    ctx_headers = {}
    for k, v in hdsr.items():
        if k.startswith(constants.FN_HTTP_PREFIX):
            ctx_headers[k.lstrip(constants.FN_HTTP_PREFIX)] = v
        else:
            ctx_headers[k] = v
    return ctx_headers


def encap_headers(headers, status=None, content_type=None):
    new_headers = {}
    for k, v in headers.items():
        if (not k.startswith(constants.CONTENT_TYPE) and
                not k.startswith(constants.CONTENT_TYPE)):
            new_headers[constants.FN_HTTP_PREFIX + k] = v

    if status is not None:
        new_headers[constants.FN_HTTP_STATUS] = str(status)
    if content_type is not None:
        new_headers[constants.CONTENT_TYPE] = content_type
    return new_headers
