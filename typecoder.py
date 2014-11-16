# -- coding: utf-8 --

import pickle as _pickle
import json as _json
import msgpack as _msgpack
import base64 as _base64

"""This module intends to build a coder system that transforms
data into _JSON- or MessagePack-able data structures.

"""

TYPE_KEY = '~_type_~'
PYPICKLE_KEY = 'pypickle'


# first we neet type coders to convert types to _jsonable objects and backwards:
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
                'bytes': bytearray(obj.data)}
    def decode(self, data):
        return self.frombuffer(data['bytes'], dtype=data['dtype'])

# second we need the coder insatnces as a list:
TYPE_CODER_LIST = [
    DateTimeCoder(),
    TimeDeltaCoder(),
    NumpyArrayCoder(),
]

# third we need routines to encode and decode the types to _msgpackable objects:
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
                       'b': bytearray(_pickle.dumps(data))}
            else:
                raise(ValueError('Type {} is not supported. '.format(
                    type(data)) + 'Enable pickle or implement a TypeCoder.'))
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

def dumps(obj,
          type_coder_list=TYPE_CODER_LIST,
          enable_pickle=False,
          type_key=TYPE_KEY,
          default=None,
          **kwargs):
    """Returns JSON string. Types encoded."""
    def default_json(obj):
        if isinstance(obj, bytearray):
            return {'~#base64': _base64.b64encode(obj).decode()}
        elif default:
            return default(obj)
        return obj
    return _json.dumps(encode_types(obj, type_coder_list, enable_pickle, type_key),
                       default=default_json, **kwargs)

def loads(data,
          type_coder_list=TYPE_CODER_LIST,
          enable_pickle=False,
          type_key=TYPE_KEY,
          **kwargs):
    """Returns data deserialized from JSON string. Types decoded."""
    def obj_hook(data):
        if (isinstance(data, dict) and
            len(data.keys())==1 and '~#base64' in data.keys()):
            return _base64.b64decode(data['~#base64'].encode())
        return data

    return decode_types(
        _json.loads(data, object_hook=obj_hook),
        type_coder_list, enable_pickle, type_key)

def packb(obj,
          type_coder_list=TYPE_CODER_LIST,
          enable_pickle=False,
          type_key=TYPE_KEY,
          default=None,
          encoding='utf-8',
          use_bin_type=True,
          **kwargs):
    """Returns MessagePack packed data. Types encoded."""
    def default_msgpack(obj):
        if isinstance(obj, bytearray):
            return bytes(obj)
        elif default:
            return default(obj)
        return obj
    return _msgpack.packb(
        encode_types(obj, type_coder_list, enable_pickle, type_key),
        encoding=encoding, use_bin_type=use_bin_type, default=default_msgpack,
        **kwargs)

def unpackb(obj,
            type_coder_list=TYPE_CODER_LIST,
            enable_pickle=False,
            type_key=TYPE_KEY,
            encoding='utf-8',
            **kwargs):
    """Returns unpacked messagepack data with types decoded."""
    return decode_types(
        _msgpack.unpackb(out_msgpack, encoding=encoding),
        type_coder_list, enable_pickle, type_key)


if __name__ == '__main__':

    from datetime import datetime
    import numpy as np

    # small test:
    # define some data:
    data = [[datetime.today()], datetime.today()- datetime.today(), np.random.randn(3), {'Hallo'}]

    # encoder and decoder:
    out = encode_types(data, TYPE_CODER_LIST, enable_pickle=True)
    res = decode_types(out, TYPE_CODER_LIST, enable_pickle=True)

    # msgpack functions:
    out_msgpack = packb(data, enable_pickle=True)
    res_msgpack = unpackb(out_msgpack, enable_pickle=True)
    for d, r in zip(data, res_msgpack): print(d==r)

    # json functions:
    out_json = dumps(data, enable_pickle=True)
    res_json = loads(out_json, enable_pickle=True)
