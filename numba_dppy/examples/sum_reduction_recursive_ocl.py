import numpy as np
from numba import int32
import numba_dppy as dppy
import math

import dpctl
import dpctl.memory as dpctl_mem


@dppy.kernel
def sum_reduction_kernel(A, input_size, partial_sums):
    local_id = dppy.get_local_id(0)
    global_id = dppy.get_global_id(0)
    group_size = dppy.get_local_size(0)
    group_id = dppy.get_group_id(0)

    local_sums = dppy.local.static_alloc(64, int32)

    local_sums[local_id] = 0

    if global_id < input_size:
        local_sums[local_id] = A[global_id]

    # Loop for computing local_sums : divide workgroup into 2 parts
    stride = group_size // 2
    while stride > 0:
        # Waiting for each 2x2 addition into given workgroup
        dppy.barrier(dppy.CLK_LOCAL_MEM_FENCE)

        # Add elements 2 by 2 between local_id and local_id + stride
        if local_id < stride:
            local_sums[local_id] += local_sums[local_id + stride]

        stride >>= 1

    if local_id == 0:
        partial_sums[group_id] = local_sums[0]


def sum_recursive_reduction(size, group_size, Dinp, Dpartial_sums):
    result = 0
    nb_work_groups = 0
    passed_size = size

    if size <= group_size:
        nb_work_groups = 1
    else:
        nb_work_groups = size // group_size
        if size % group_size != 0:
            nb_work_groups += 1
            passed_size = nb_work_groups * group_size

    sum_reduction_kernel[passed_size, group_size](Dinp, size, Dpartial_sums)

    if nb_work_groups <= group_size:
        sum_reduction_kernel[group_size, group_size](
            Dpartial_sums, nb_work_groups, Dinp
        )
        result = Dinp[0]
    else:
        result = sum_recursive_reduction(nb_work_groups, group_size, Dpartial_sums, Dinp)

    return result


def get_context():
    if dpctl.has_gpu_queues():
        return "opencl:gpu"
    elif dpctl.has_cpu_queues():
        return "opencl:cpu"
    else:
        raise RuntimeError("No device found")


def sum_reduce(A):
    global_size = len(A)
    work_group_size = 64
    nb_work_groups = global_size // work_group_size
    if (global_size % work_group_size) != 0:
        nb_work_groups += 1

    partial_sums = np.zeros(nb_work_groups).astype(A.dtype)

    context = get_context()
    with dpctl.device_context(context):
        inp_buf = dpctl_mem.MemoryUSMShared(A.size * A.dtype.itemsize)
        inp_ndarray = np.ndarray(A.shape, buffer=inp_buf, dtype=A.dtype)
        np.copyto(inp_ndarray, A)

        partial_sums_buf = dpctl_mem.MemoryUSMShared(
            partial_sums.size * partial_sums.dtype.itemsize
        )
        partial_sums_ndarray = np.ndarray(
            partial_sums.shape, buffer=partial_sums_buf, dtype=partial_sums.dtype
        )
        np.copyto(partial_sums_ndarray, partial_sums)

        result = sum_recursive_reduction(
            global_size, work_group_size, inp_ndarray, partial_sums_ndarray
        )

    return result


def test_sum_reduce():
    N = 20000

    A = np.ones(N).astype(np.int32)

    print("Running recursive reduction")

    actual = sum_reduce(A)
    expected = N

    print("Actual:  ", actual)
    print("Expected:", expected)

    assert actual == expected


if __name__ == "__main__":
    test_sum_reduce()
