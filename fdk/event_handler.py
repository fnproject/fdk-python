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

import io
import logging
import os
import sys

from fdk import constants

from fdk.async_http import response

logger = logging.getLogger(__name__)

fn_logframe_name = os.environ.get(constants.FN_LOGFRAME_NAME)
fn_logframe_hdr = os.environ.get(constants.FN_LOGFRAME_HDR)


def event_handle(handle_code):
    """
    Performs HTTP request-response procedure
    :param handle_code: customer's code
    :type handle_code: fdk.customer_code.Function
    :return: None
    """
    async def pure_handler(request):
        from fdk import runner
        logger.info("in pure_handler")
        headers = dict(request.headers)
        log_frame_header(headers)
        func_response = await runner.handle_request(
            handle_code, constants.HTTPSTREAM,
            headers=headers, data=io.BytesIO(request.body))
        logger.info("request execution completed")

        headers = func_response.context().GetResponseHeaders()
        status = func_response.status()
        if status not in constants.FN_ENFORCED_RESPONSE_CODES:
            status = constants.FN_DEFAULT_RESPONSE_CODE

        return response.HTTPResponse(
            headers=headers,
            status=status,
            content_type=headers.get(constants.CONTENT_TYPE),
            body_bytes=func_response.body_bytes(),
        )

    return pure_handler


def log_frame_header(headers):
    if all((fn_logframe_name, fn_logframe_hdr)):
        frm = fn_logframe_hdr.lower()
        if frm in headers:
            id = headers.get(frm)
            frm = "\n{}={}\n".format(fn_logframe_name, id)
            print(frm, file=sys.stderr, flush=True)
            print(frm, file=sys.stdout, flush=True)
