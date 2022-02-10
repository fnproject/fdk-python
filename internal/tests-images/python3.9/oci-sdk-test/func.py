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
import oci
from fdk import response


def handler(ctx, data: io.BytesIO = None):
    # send request to identity client to get compartment
    compartment_id = ""
    try:
        body = json.loads(data.getvalue())
        compartment_id = body.get("compartmentId")
        signer = oci.auth.signers.get_resource_principals_signer()
        identity_client = oci.identity.IdentityClient(
            config={},
            signer=signer
        )
        result = identity_client.get_compartment(
            compartment_id=compartment_id
        ).data.id

    except Exception as ex:
        result = "Exception in sending request to identity client for " + \
                 "compartmentId " + compartment_id + " : " + str(ex)

    return response.Response(
        ctx, response_data=json.dumps(
            {"compartmentId": result}, separators=(',', ':')),
        headers={"Content-Type": "application/json"}
    )
