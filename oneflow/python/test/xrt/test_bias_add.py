import unittest
import numpy as np

import oneflow as flow

def make_job(x_shape, b_shape, dtype=flow.float32):
    @flow.function
    def bias_add_job(x = flow.input_blob_def(x_shape, dtype=dtype),
                     bias = flow.input_blob_def(b_shape, dtype=dtype)):
        flow.config.use_xla_jit(False)
        flow.config.use_tensorrt(False)
        return flow.nn.bias_add(x, bias)
    return bias_add_job

def make_xla_job(x_shape, b_shape, dtype=flow.float32):
    @flow.function
    def xla_bias_add_job(x = flow.input_blob_def(x_shape, dtype=dtype),
                     bias = flow.input_blob_def(b_shape, dtype=dtype)):
        flow.config.use_xla_jit(True)
        flow.config.use_tensorrt(False)
        return flow.nn.bias_add(x, bias)
    return xla_bias_add_job


class TestBiasAdd(unittest.TestCase):
    def _test_body(self, x, bias, dtype=np.float32):
        f1 = make_job(x.shape, bias.shape, dtype=flow.float32)
        f2 = make_xla_job(x.shape, bias.shape, dtype=flow.float32)
        a = f1(x, bias).get()
        b = f2(x, bias).get()
        print("without xla: ", a)
        print("with xla", b)
        self.assertTrue(np.allclose(a, b , rtol=1e-03, atol=1e-05))

        flow.clear_default_session()

    def _test_ones_body(self, x_shape, bias_shape, dtype=np.float32):
        x = np.ones(x_shape, dtype=dtype)
        b = np.ones(bias_shape, dtype=dtype)
        self._test_body(x, b, dtype=dtype)

    def _test_random_body(self, x_shape, bias_shape, dtype=np.float32):
        x = np.random.random(x_shape).astype(dtype)
        b = np.random.random(bias_shape).astype(dtype)
        self._test_body(x, b, dtype=dtype)

    def test_ones_input(self):
        self._test_ones_body((1, 10), (10))
        self._test_ones_body((2, 10, 2), (10))
        self._test_ones_body((2, 5, 2, 2), (5))

    def test_random_input(self):
        self._test_random_body((1, 10), (10))
        self._test_random_body((2, 10, 2), (10))
        self._test_random_body((2, 5, 2, 2), (5))

if __name__ == '__main__':
    unittest.main()