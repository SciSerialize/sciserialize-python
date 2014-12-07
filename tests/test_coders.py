from sciserialize import coders

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

class TestSetCoder:
    set_coder = coders.SetCoder()
    test_data = {'hello', 1}
    def test_verifyer(self):
        assert(self.set_coder.verify_type(self.test_data) == True)
        assert(self.set_coder.verify_type([self.test_data]) == False)
    def test_coder(self):
        assert(
            self.set_coder.decode(
            self.set_coder.encode(
                self.test_data)) == self.test_data)
