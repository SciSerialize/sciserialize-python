import sys
sys.path.append('..')

from sciserialize import serializers
import numpy as np


class TestSerializers:
    test_data = np.random.randn(10, 3, 2)

    def test_dumps_loads(self):
        s = serializers.dumps(self.test_data)
        assert np.all(self.test_data == serializers.loads(s))

    def test_dump_load(self):
        fname = '#test.json#'
        with open(fname, 'w') as f:
            serializers.dump(self.test_data, f)
        with open(fname, 'r') as f:
            d = serializers.load(f)
        assert np.all(d == self.test_data)

    def test_packb_unpackb(self):
        s = serializers.packb(self.test_data)
        assert np.all(self.test_data == serializers.unpackb(s))

    def test_pack_unpack(self):
        fname = '#test.mpk#'
        with open(fname, 'wb') as f:
            serializers.pack(self.test_data, f)
        with open(fname, 'rb') as f:
            d = serializers.unpack(f)
        assert np.all(d == self.test_data)
