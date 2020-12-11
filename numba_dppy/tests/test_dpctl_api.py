import unittest
import dpctl


@unittest.skipUnless(dpctl.has_gpu_queues(), 'test only on GPU system')
class TestDPCTLAPI(unittest.TestCase):
    def test_dpctl_api(self):
        with dpctl.device_context("opencl:gpu") as gpu_queue:
            dpctl.dump()
            dpctl.get_current_queue()
            dpctl.get_num_platforms()
            dpctl.get_num_activated_queues()
            dpctl.has_cpu_queues()
            dpctl.has_gpu_queues()
            dpctl.has_sycl_platforms()
            dpctl.is_in_device_context()


if __name__ == '__main__':
    unittest.main()
