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

import json
import io
import pytest

from fdk import fixtures
from fdk import response


def handler(ctx, data: io.BytesIO = None):
    name = "World"
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        print(str(ex))
        pass

    return response.Response(
        ctx, status_code=202, response_data=json.dumps(
            {"message": "Hello {0}".format(name)}),
        headers={"Content-Type": "application/json"}
    )


@pytest.mark.asyncio
async def test_parse_request_without_data():
    call = await fixtures.setup_fn_call(handler)

    content, status, headers = await call

    assert 202 == status
    assert {"message": "Hello World"} == json.loads(content)
