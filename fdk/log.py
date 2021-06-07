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

import logging
import os
import sys
from contextvars import ContextVar


__fn_request_id__ = ContextVar("fn_request_id", default=None)


def set_request_id(rid):
    __fn_request_id__.set(rid)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.fn_request_id = __fn_request_id__.get()
        return super().format(record)


def __setup_logger():
    fdk_debug = os.environ.get("FDK_DEBUG") in [
        'true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

    logging.getLogger("asyncio").setLevel(logging.WARNING)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stderr)
    formatter = RequestFormatter(
        '%(fn_request_id)s - '
        '%(name)s - '
        '%(levelname)s - '
        '%(message)s'
    )
    ch.setFormatter(formatter)
    root.addHandler(ch)
    logger = logging.getLogger("fdk")
    if fdk_debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    return logger


__log__ = __setup_logger()


def get_logger():
    return __log__


def log(message):
    __log__.debug(message)


__request_log__ = logging.getLogger('fn')


def get_request_log():
    return __request_log__
