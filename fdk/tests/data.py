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


http_request_with_query_and_data = """GET /v1/apps?something=something&etc=etc HTTP/1.1\r
Host: localhost:8080\r
Content-Length: 11\r
Content-Type: application/x-www-form-urlencoded\r
User-Agent: curl/7.51.0\r
\r
hello:hello
"""


http_request_no_data = """GET /v1/apps?something=something&etc=etc HTTP/1.1\r
Host: localhost:8080\r
User-Agent: curl/7.51.0\r
Accept: */*\r
"""

http_request_no_query = """GET /v1/apps HTTP/1.1\r
Host: localhost:8080\r
User-Agent: curl/7.51.0\r
Accept: */*\r
"""

http_coerce = """POST /r/emokognition/detect HTTP/1.1\r
Host: localhost:9000\r
Fn_header_accept: */*\r
Fn_header_content_length: 46\r
Fn_header_content_type: application/json\r
Fn_header_user_agent: curl/7.54.0\r
\r
{"media_url": "http://localhost:8080/img.png"}
"""

http_request_with_fn_content_headers = """POST /r/emokognition/detect HTTP/1.1\r
Host: localhost:9000\r
Fn_header_accept: */*\r
Fn_header_content_length: 46\r
Fn_header_content_type: application/x-www-form-urlencoded\r
Fn_header_user_agent: curl/7.54.0\r
\r
{"media_url": "http://localhost:8080/img.png"}
"""

http_with_deadline = """GET /v1/apps?something=something&etc=etc HTTP/1.1\r
Host: localhost:8080\r
Content-Length: 11\r
Content-Type: application/x-www-form-urlencoded\r
User-Agent: curl/7.51.0\r
Fn_deadline: {}\r
\r
hello:hello
"""

json_request_with_data = (
    '{\n"call_id":"some_id"\n,'
    '"content_type":"application/json"\n'
    ',"type":"sync"\n'
    ',"body":"{\\"a\\":\\"a\\"}\n"\n'
    ',"protocol":{"type":"http"\n'
    ',"request_url":"/v1/apps?something=something&etc=etc"\n'
    ',"headers":{"Content-Type":["application/json"],'
    '"Host":["localhost:8080"],"User-Agent":["curl/7.51.0"]}\n'
    '\n}\n}\n\n')

json_request_without_data = (
    '{\n"call_id":"some_id"\n,'
    '"content_type":"application/json"\n'
    ',"type":"sync"\n'
    ',"deadline":"0001-01-01T00:00:00.000Z"\n'
    ',"body":""\n'
    ',"protocol":{"type":"http"\n'
    ',"request_url":"/v1/apps?something=something&etc=etc"\n'
    ',"headers":{"Content-Type":["application/json"],'
    '"Host":["localhost:8080"],"User-Agent":["curl/7.51.0"]}\n'
    '\n}\n}\n\n')

json_with_deadline = [
    '{\n"call_id":"some_id"\n,'
    '"content_type":"application/json"\n'
    ',"type":"sync"\n',
    ',"body":"{\\"a\\":\\"a\\"}\n"\n'
    ',"protocol":{"type":"http"\n'
    ',"request_url":"/v1/apps?something=something&etc=etc"\n'
    ',"headers":{"Content-Type":["application/json"],'
    '"Host":["localhost:8080"],"User-Agent":["curl/7.51.0"]}\n'
    '\n}\n}\n\n']
