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

import fdk
import os
import sys

from fdk import customer_code


def main():
    if len(sys.argv) < 1:
        print("Usage: fdk <func_module> [entrypoint]")
        sys.exit("at least func module must be specified")

    if not os.path.exists(sys.argv[1]):
        sys.exit("Module: {0} doesn't exist".format(sys.argv[1]))

    if len(sys.argv) > 2:
        handler = customer_code.Function(
            sys.argv[1], entrypoint=sys.argv[2])
    else:
        handler = customer_code.Function(sys.argv[1])

    fdk.handle(handler)
