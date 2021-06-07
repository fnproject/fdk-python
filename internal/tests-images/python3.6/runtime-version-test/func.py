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
import logging
import io


def handler(ctx, data: io.BytesIO = None):
    python_version = ""
    try:
        python_version = "python" + (str(sys.version_info.major)
                                     + "."
                                     + str(sys.version_info.minor)
                                     + "."
                                     + str(sys.version_info.micro)
                                     )
    except Exception as ex:
        logging.getLogger().info(
            'Error while determining python runtime version: ' + str(ex)
        )
    return python_version
