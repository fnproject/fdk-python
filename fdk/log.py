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

import logging
import os
import sys


def __setup_logger():
    fdk_debug = os.environ.get("FDK_DEBUG") in [
        'true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

    logging.getLogger("asyncio").setLevel(logging.WARNING)
    root = logging.getLogger()
    if fdk_debug:
        root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        '%(asctime)s - '
        '%(name)s - '
        '%(levelname)s - '
        '%(message)s'
    )
    ch.setFormatter(formatter)
    root.addHandler(ch)
    logger = logging.getLogger("fdk")
    return logger


__log__ = __setup_logger()


def get_logger():
    return __log__


def log(message):
    __log__.debug(message)
