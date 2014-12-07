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
        assert(self.type_coder.verify_type('test'))
        assert(self.type_coder.verify_type(1) == False)
