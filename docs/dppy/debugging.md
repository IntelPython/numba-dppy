## Debugging with GDB

Numba-dppy allows GPU kernels to be debugged with the GDB debugger.
Setting the debug environment variable `NUMBA_DPPY_DEBUG` (e.g. `export NUMBA_DPPY_DEBUG=True`) enables
the emission of debug information.
To disable debugging set this variable to None: (e.g. `export NUMBA_DPPY_DEBUG= `).

Unlike the CPU target, currently the following debug information is available:
- Source location (filename and line number).
- Setting break points by the line number.
- Stepping over break points.

### Requirements

Intel® Distribution for GDB installed to the system.
Documentation for the GDB debugger can be found in the
[Intel® Distribution for GDB documentation](https://software.intel.com/content/www/us/en/develop/tools/oneapi/components/distribution-for-gdb.html).

### Example debug usage

```bash
$ export NUMBA_DPPY_DEBUG=True
$ gdb-oneapi -q python
(gdb) break numba_dppy/examples/sum.py:14     # Assumes the kernel is in file sum.py, at line 14
(gdb) run sum.py
```

For example, given the following Numba-dppy kernel code:
```python
import numpy as np
import numba_dppy as dppy
import dpctl

@dppy.kernel
def data_parallel_sum(a, b, c):
    i = dppy.get_global_id(0)
    c[i] = a[i] + b[i]

global_size = 10
N = global_size

a = np.array(np.random.random(N), dtype=np.float32)
b = np.array(np.random.random(N), dtype=np.float32)
c = np.ones_like(a)

with dpctl.device_context("opencl:gpu") as gpu_queue:
    data_parallel_sum[global_size, dppy.DEFAULT_LOCAL_SIZE](a, b, c)
```

GDB output:
```bash
Thread 2.2 hit Breakpoint 1,  with SIMD lanes [0-7], dppl_py_devfn__5F__5F_main_5F__5F__2E_data_5F_parallel_5F_sum_24_1_2E_array_28_float32_2C__20_1d_2C__20_C_29__2E_array_28_float32_2C__20_1d_2C__20_C_29__2E_array_28_float32_2C__20_1d_2C__20_C_29_ () at sum.py:14
14          i = dppy.get_global_id(0)
(gdb)
(gdb) n  # Making step
15          c[i] = a[i] + b[i]
```


### Limitations

Currently, Numba-dppy provides only initial support of debugging GPU kernels.
The following functionality is **not supported** :
- Printing kernel local variables (e.g. ```info locals```).
- Stepping over several off-loaded functions.