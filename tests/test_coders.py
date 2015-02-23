import sys
sys.path.append('..')

from sciserialize import coders
import datetime
import numpy as np
import pandas as pd


# Maybe test_data could be more tha one...

class TestTypeCoder:
    """Tests the base class TypeCoder."""

    class MyTypeCoder(coders.TypeCoder):
        type_ = type('test')

    type_coder = MyTypeCoder()

    def test_attributes(self):
        for attr in ['encode', 'decode', 'type_', 'typestr', 'verify_type']:
            assert(hasattr(self.type_coder, attr))
        assert(hasattr(self.type_coder.verify_type, '__call__'))

    def test_verify_type_method(self):
        assert(self.type_coder.verify_type('test') == True)
        assert(self.type_coder.verify_type(1) == False)


class TestCoder:
    coder = coders.SetCoder()
    test_data = {'hello', 1, 2.3}
    test_data_false = [1, 2, 3]

    def test_verifier(self):
        assert(self.coder.verify_type(self.test_data) == True)
        assert(self.coder.verify_type(self.test_data_false) == False)

    def test_coder(self):
        assert(np.all(
            self.coder.decode(
                self.coder.encode(
                    self.test_data)) == self.test_data))


class TestSetCoder(TestCoder):
    coder = coders.SetCoder()
    test_data = {'hello', 1, 2.3}
    test_data_false = (1, 4, 6)


class TestDateTimeIsoStringCoder(TestCoder):
    coder = coders.DateTimeIsoStringCoder()
    test_data = datetime.datetime.now()
    test_data_false = {1, 3, 5, datetime.datetime.now()}


class TestTimeDeltaCoder(TestCoder):
    coder = coders.TimeDeltaCoder()
    test_data = datetime.datetime.now() - datetime.datetime.now()
    test_data_false = (5, datetime.datetime.now())


class TestNumpyArrayCoder(TestCoder):
    coder = coders.NumpyArrayCoder()
    test_data = np.random.randn(7, 8, 9, 2)
    test_data_false = np.int16(19)


class TestNumpyMaskedArrayCoder(TestCoder):
    coder = coders.NumpyMaskedArrayCoder()
    test_data = np.ma.masked_array(np.random.randn(3), [True, False, True])
    test_data_false = np.int16(19)


class TestDataFrameCoder(TestCoder):
    coder = coders.DataFrameCoder()
    test_data = pd.DataFrame(np.random.randn(19, 3), columns=['A', 'Be', 10])
    test_data_false = np.ma.masked_array(np.random.randn(3),
                                         [True, False, True])


if __name__ == '__main__':
    import pytest

    pytest.main()
