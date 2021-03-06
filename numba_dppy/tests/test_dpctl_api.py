# Copyright 2021 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import dpctl
from numba_dppy.tests._helper import skip_test


list_of_filter_strs = [
    "opencl:gpu:0",
    "level_zero:gpu:0",
    "opencl:cpu:0",
]


@pytest.fixture(params=list_of_filter_strs)
def filter_str(request):
    return request.param


def test_dpctl_api(filter_str):
    if skip_test(filter_str):
        pytest.skip()

    with dpctl.device_context(filter_str):
        dpctl.lsplatform()
        dpctl.get_current_queue()
        dpctl.get_num_activated_queues()
        dpctl.is_in_device_context()
