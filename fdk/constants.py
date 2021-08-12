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

import sys
from fdk import version

ASYNC_IO_READ_BUFFER = 65536
DEFAULT_DEADLINE = 30

HTTPSTREAM = "http-stream"
INTENT_HTTP_REQUEST = "httprequest"

# env vars
FN_FORMAT = "FN_FORMAT"
FN_LISTENER = "FN_LISTENER"
FN_APP_ID = "FN_APP_ID"
FN_ID = "FN_FN_ID"
FN_LOGFRAME_NAME = "FN_LOGFRAME_NAME"
FN_LOGFRAME_HDR = "FN_LOGFRAME_HDR"
FN_APP_NAME = "FN_APP_NAME"
FN_NAME = "FN_FN_NAME"
OCI_TRACE_COLLECTOR_URL = "OCI_TRACE_COLLECTOR_URL"
OCI_TRACING_ENABLED = "OCI_TRACING_ENABLED"


# headers are lower case TODO(denis): why?
FN_INTENT = "fn-intent"
FN_HTTP_PREFIX = "fn-http-h-"
FN_HTTP_STATUS = "fn-http-status"
FN_DEADLINE = "fn-deadline"
FN_FDK_VERSION = "fn-fdk-version"
FN_FDK_RUNTIME = "fn-fdk-runtime"
FN_HTTP_REQUEST_URL = "fn-http-request-url"
FN_CALL_ID = "fn-call-id"
FN_HTTP_METHOD = "fn-http-method"
CONTENT_TYPE = "content-type"
CONTENT_LENGTH = "content-length"
X_B3_TRACEID = "x-b3-traceid"
X_B3_SPANID = "x-b3-spanid"
X_B3_PARENTSPANID = "x-b3-parentspanid"
X_B3_SAMPLED = "x-b3-sampled"
X_B3_FLAGS = "x-b3-flags"

FN_ENFORCED_RESPONSE_CODES = [200, 502, 504]
FN_DEFAULT_RESPONSE_CODE = 200

VERSION_HEADER_VALUE = "fdk-python/" + version.VERSION
RUNTIME_HEADER_VALUE = "python/{}.{}.{} {}".format(
    sys.version_info.major, sys.version_info.minor, sys.version_info.micro,
    sys.version_info.releaselevel)


# todo: python 3.8 is on its way, make more flexible
def is_py37():
    py_version = sys.version_info
    return (py_version.major, py_version.minor) == (3, 7)
