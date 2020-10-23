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

import pytest

from fdk import constants
from fdk import customer_code

from fdk.tests import funcs


@pytest.mark.skipif(constants.is_py37(),
                    reason="this test is for Python 3.5.2+ only")
def test_py352plus():
    dm = customer_code.Python35plusDelayedImport(funcs.__file__)
    assert dm.executed is False

    m = dm.get_module()
    assert dm.executed is True
    assert m is not None


@pytest.mark.skipif(not constants.is_py37(),
                    reason="this test is for Python 3.7.1+ only")
def test_py37():
    dm = customer_code.Python37DelayedImport(funcs.__file__)
    assert dm.executed is False

    m = dm.get_module()
    assert dm.executed is True
    assert m is not None


def test_generic_delayed_loader():
    f = customer_code.Function(
        funcs.__file__, entrypoint="content_type")
    assert f is not None
    assert f._delayed_module_class.executed is False

    h = f.handler()
    assert h is not None
    assert f._delayed_module_class.executed is True
