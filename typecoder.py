# -- coding: utf-8 --

import pickle
import json
import msgpack

"""This module intends to build a coder system that transforms
data into JSON- or MessagePack-able data structures.

"""

TYPE_KEY = '~_type_~'
PYPICKLE_KEY = 'pypickle'


# first we neet type coders to convert types to jsonable objects and backwards:
# these definitions could be outsourced to coders.py and finally the
# TYPE_CODER_LIST could be generated automaticaly by appending all abjects
# with the attributes type_, typestr, encode, decode.

class DateTimeCoder:
    from datetime import datetime
    import dateutil.parser
    type_ = datetime
    typestr = 'datetime'
    def encode(self, obj):
        return {'isostr': datetime.isoformat(obj)}
    def decode(self, data):
        return self.dateutil.parser.parse(data['isostr'])

class TimeDeltaCoder:
    from datetime import timedelta
    type_ = timedelta
    typestr = 'timedelta'
    def encode(self, obj):
        return {'days': obj.days,
                'seconds': obj.seconds,
                'microsec': obj.microseconds}
    def decode(self, data):
        return self.timedelta(data['days'], data['seconds'], data['microsec'])

class NumpyArrayCoder:
    #TODO: correct binary serialization
    # i was a bit confused whats the right way to do
    from numpy import ndarray, frombuffer
    type_ = ndarray
    typestr = 'ndarray'
    def encode(self, obj):
        return {'dtype': str(obj.dtype),
                'shape': list(obj.shape),
                'valuebytes': bytes(obj.data)}
    def decode(self, data):
        return self.frombuffer(data['valuebytes'], dtype=data['dtype'])

# second we need the coder insatnces as a list:
TYPE_CODER_LIST = [
    DateTimeCoder(),
    TimeDeltaCoder(),
    NumpyArrayCoder(),
]

# third we need routines to encode and decode the types to msgpackable objects:
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
        else:
            for coder in type_coder_list:
                if isinstance(data, coder.type_):
                    out = {type_key: coder.typestr}
                    out.update(coder.encode(data))
                    return out
            if enable_pickle:
                out = {type_key: PYPICKLE_KEY,
                       's': pickle.dumps(data)}
            else:
                raise(ValueError('Type {} is not supported.' +
                    'Enable pickle or implement a TypeCoder.'.format(
                    type(data))))
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
                return type_coder_list[index].decode(data)
            elif enable_pickle and typestr==PYPICKLE_KEY:
                out = pickle.loads(data['s'])
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


# small test
from datetime import datetime
import numpy as np
data = [[datetime.today()], datetime.today()- datetime.today(), np.random.randn(3), {'Hallo'}]
out = encode_types(data, TYPE_CODER_LIST, enable_pickle=True)
res = decode_types(out, TYPE_CODER_LIST, enable_pickle=True)

out_msgpack = msgpack.packb(out, encoding='utf-8', use_bin_type=True)
res_msgpack = decode_types(msgpack.unpackb(out_msgpack, encoding='utf-8'), enable_pickle=True)
for d, r in zip(data, res_msgpack): print(d==r)

# TODO: for json we need a ste between to convert binary data to base64 strings...
#out_json = json.dumps(out)
#res_json = json.loads(out_json)
