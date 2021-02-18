################################################################################
#                                 Numba-DPPY
#
# Copyright 2020-2021 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import dpctl
import numpy as np
from numba import njit
import pytest
from numba_dppy.testing import ensure_dpnp, dpnp_debug

list_of_filter_strs = [
    "opencl:gpu:0",
    "level0:gpu:0",
    "opencl:cpu:0",
]


@pytest.fixture(params=list_of_filter_strs)
def filter_str(request):
    return request.param


list_of_dtypes = [
    np.int32,
    np.int64,
    np.float32,
    np.float64,
]

@pytest.fixture(params=list_of_dtypes)
def input_arrays(request):
    # The size of input and out arrays to be used
    N = 10
    a = np.array(np.random.random(N), request.param)
    b = np.array(np.random.random(N), request.param)
    return a, b

list_of_unary_ops = [
    "sum",
    "prod",
    "max",
    "min",
    "mean",
    "argmax",
    "argmin",
    "argsort",
]

@pytest.fixture(params=list_of_unary_ops)
def unary_op(request):
    func_str = "def fn(a):\n    return a." + request.param + "()"
    ldict = {}
    exec(func_str, globals(), ldict)
    fn = ldict["fn"]
    return fn

def test_unary_ops(filter_str, unary_op, input_arrays, capfd):
    try:
        with dpctl.device_context(filter_str):
            pass
    except Exception:
        pytest.skip()

    if not ensure_dpnp():
        pytest.skip()

    a = input_arrays[0]
    actual = np.empty(shape=a.shape, dtype=a.dtype)
    expected = np.empty(shape=a.shape, dtype=a.dtype)


    f = njit(unary_op)
    with dpctl.device_context(filter_str), dpnp_debug():
        actual = f(a)
        captured = capfd.readouterr()
        assert "dpnp implementation" in captured.out

    expected = unary_op(a)
    c = a.argsort()
    np.testing.assert_allclose(actual, expected, rtol=1e-3, atol=0)
