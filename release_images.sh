#!/usr/bin/env bash
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


user="fnproject"
image="python"

runtime36="3.6"
docker push ${user}/${image}:${runtime36}
docker push ${user}/${image}:${runtime36}-dev

runtime371="3.7.1"
docker push ${user}/${image}:${runtime371}
docker push ${user}/${image}:${runtime371}-dev

runtime37="3.7"
docker push ${user}/${image}:${runtime37}
docker push ${user}/${image}:${runtime37}-dev

runtime385="3.8.5"
docker push ${user}/${image}:${runtime385}
docker push ${user}/${image}:${runtime385}-dev

runtime38="3.8"
docker push ${user}/${image}:${runtime38}
docker push ${user}/${image}:${runtime38}-dev
