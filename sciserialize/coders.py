# -- coding: utf-8 --
import warnings as _warnings
import pickle as _pickle


TYPE_KEY = '__type__'
PYPICKLE_TYPE_NAME = 'pypickle'


## Define type coder classes that allows to encode and decode
## specific data types:
## bytes must be encoded as bytearrays so the serializers can
## convert them to the binary representation in the serialization format.
## (for instance JSON has no binary type so bytearrays need to be converted
## to base64 strings)
class TypeCoder:
    type_ = None
    typestr = None
    def verify_type(self, obj):
        """Returns a boolean if `type_` ist an instance of `self.type_`.
        If you need a more explicit verification of your type,
        you can reimlement this function.
        """
        return isinstance(obj, self.type_)
    def encode(self, obj):
        pass
    def decode(self, data):
        pass
    def __repr__(self):
        return str(self.__class__)

class SetCoder(TypeCoder):
    type_ = set
    typestr = 'unique_set'
    def encode(self, obj):
        return {TYPE_KEY: self.typestr,
                'set': list(obj)}
    def decode(self, data):
        return set(data['set'])

class DateTimeIsoStringCoder(TypeCoder):
    from datetime import datetime
    import dateutil.parser
    type_ = datetime
    typestr = 'datetime'
    def encode(self, obj):
        return {TYPE_KEY: self.typestr,
                'isostr': self.datetime.isoformat(obj)}
    def decode(self, data):
        return self.dateutil.parser.parse(data['isostr'])

class TimeDeltaCoder(TypeCoder):
    from datetime import timedelta
    type_ = timedelta
    typestr = 'timedelta'
    def encode(self, obj):
        return {TYPE_KEY: self.typestr,
                'days': obj.days,
                'seconds': obj.seconds,
                'microsec': obj.microseconds}
    def decode(self, data):
        return self.timedelta(data['days'], data['seconds'], data['microsec'])

class NumpyArrayCoder(TypeCoder):
    from numpy import ndarray, frombuffer, array
    type_ = ndarray
    typestr = 'ndarray'
    def encode(self, obj):
        if obj.dtype==object:
            data = encode_types(obj.tolist())
        else:
            data = bytearray(obj.data)
        return {TYPE_KEY: self.typestr,
                'dtype': str(obj.dtype),
                'shape': [int(sh) for sh in obj.shape],
                'bytes': data}
    def decode(self, data):
        if data['dtype'] == 'object':
            return self.array(decode_types(data['bytes']),
                              dtype=data['dtype']).reshape(data['shape'])
        else:
            return self.frombuffer(data['bytes'],
                                   dtype=data['dtype']).reshape(data['shape'])

class NumpyMaskedArrayCoder(TypeCoder):
    from numpy.ma import masked_array
    from numpy import frombuffer
    type_ = masked_array
    typestr = 'maskedarray'
    ndarray_coder = NumpyArrayCoder()
    def encode(self, obj):
        d = self.ndarray_coder.encode(obj)
        d[TYPE_KEY] = self.typestr
        d['mask_bytes'] = bytearray(obj.mask.data)
        return d
    def decode(self, data):
        mask = self.frombuffer(data['mask_bytes'], dtype=bool)
        return self.masked_array(self.ndarray_coder.decode(data), mask)


## Initialize all implemented coder instances into a coder list:
TYPE_CODER_LIST = []
try:
    TYPE_CODER_LIST.append(SetCoder())
except:
    _warnings.warn('SetCoder could not be loaded')
try:
    TYPE_CODER_LIST.append(DateTimeIsoStringCoder())
except:
    _warnings.warn('DateTimeIsoStrinCoder could not be loaded')
try:
    TYPE_CODER_LIST.append(TimeDeltaCoder())
except:
    _warnings.warn('TimeDeltaCoder could not be loaded')
try:
    TYPE_CODER_LIST.append(NumpyArrayCoder())
except:
    _warnings.warn('NumpyArrayCoder could not be loaded')
try:
    TYPE_CODER_LIST.append(NumpyMaskedArrayCoder())
except:
    _warnings.warn('NumpyMaskedArrayCoder could not be loaded')


## Define Type encoders, that uses the coder list to encode and decode the data:
def encode_types(data,
                 type_coder_list=TYPE_CODER_LIST,
                 enable_pickle=False,
                 type_key=TYPE_KEY):
    """Recursive type encoder."""
    def _recursive_encoder(data):
        if isinstance(data, dict):
            out = {}
            for key in data:
                out[key] = _recursive_encoder(data[key])
        elif isinstance(data, (list, tuple)):
            out = list(data)
            for index in range(len(out)):
                out[index] = _recursive_encoder(data[index])
        elif isinstance(data, (str, int, float)):
            return data
        else:
            for coder in type_coder_list:
                if coder.verify_type(data):
                    return coder.encode(data)
            if enable_pickle:
                out = {type_key: PYPICKLE_TYPE_NAME,
                       'b': bytearray(_pickle.dumps(data))}
            else:
                raise(ValueError('Type {}  with value {} is not supported. '.format(
                    type(data), data) + 'Enable pickle or implement a TypeCoder.'))
        return out
    return _recursive_encoder(data)

def decode_types(data,
                 type_coder_list=TYPE_CODER_LIST,
                 enable_pickle=False,
                 type_key=TYPE_KEY):
    """Recursive type decoder."""
    supported_typestr_list = [o.typestr for o in type_coder_list]
    def _recursive_decoder(data):
        if isinstance(data, dict) and type_key in data:
            data = data.copy()
            typestr = data.pop(type_key)
            if typestr in supported_typestr_list:
                index = supported_typestr_list.index(typestr)
                return _recursive_decoder(type_coder_list[index].decode(data))
            elif enable_pickle and typestr==PYPICKLE_TYPE_NAME:
                out = _pickle.loads(data['b'])
            else:
                out = _recursive_decoder(data)
                out[type_key] = typestr
                return out
        elif isinstance(data, dict):
            out = {}
            for key in data:
                out[key] = _recursive_decoder(data[key])
        elif isinstance(data, (list, tuple)):
            out = list(data)
            for index in range(len(out)):
                out[index] = _recursive_decoder(data[index])
        else:
            out = data
        return out
    return _recursive_decoder(data)
