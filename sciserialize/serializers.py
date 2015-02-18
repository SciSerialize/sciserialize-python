# -- encoding: utf-8 --
import json as _json
import msgpack as _msgpack
import base64 as _base64

from .coders import (encode_types, decode_types, TYPE_CODER_LIST, TYPE_KEY)


BASE64_KEY = '__base64__'
ENABLE_PICKLE = False


def dumps(obj,
          enable_pickle=ENABLE_PICKLE,
          type_coder_list=TYPE_CODER_LIST,
          type_key=TYPE_KEY,
          default=None,
          **kwargs):
    """Returns JSON string. Types encoded."""
    def default_json(obj):
        if isinstance(obj, bytearray):
            return {BASE64_KEY: _base64.b64encode(obj).decode()}
        elif default:
            return default(obj)
        return obj
    return _json.dumps(encode_types(
        obj, type_coder_list, enable_pickle, type_key),
        default=default_json, **kwargs)

dumps.__doc__ = ''.join((dumps.__doc__, '\n\nJSON-Doc:\n',
                         _json.dumps.__doc__))


def loads(data,
          enable_pickle=ENABLE_PICKLE,
          type_coder_list=TYPE_CODER_LIST,
          type_key=TYPE_KEY,
          **kwargs):
    """Returns data deserialized from JSON string. Types decoded."""
    def obj_hook(data):
        if (isinstance(data, dict) and
                len(data.keys()) == 1 and BASE64_KEY in data.keys()):
            return _base64.b64decode(data[BASE64_KEY].encode())
        return data
    return decode_types(
        _json.loads(data, object_hook=obj_hook),
        type_coder_list, enable_pickle, type_key)

loads.__doc__ = ''.join((loads.__doc__, '\n\nJSON-Doc:\n',
                         _json.loads.__doc__))


def packb(obj,
          enable_pickle=ENABLE_PICKLE,
          type_coder_list=TYPE_CODER_LIST,
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

packb.__doc__ = ''.join((packb.__doc__, '\n\nMesssagePack-Doc:\n',
                         _msgpack.packb.__doc__))


def unpackb(obj,
            enable_pickle=ENABLE_PICKLE,
            type_coder_list=TYPE_CODER_LIST,
            type_key=TYPE_KEY,
            encoding='utf-8',
            **kwargs):
    """Returns unpacked messagepack data with types decoded."""
    return decode_types(
        _msgpack.unpackb(obj, encoding=encoding),
        type_coder_list, enable_pickle, type_key)

unpackb.__doc__ = ''.join((unpackb.__doc__, '\n\nMesssagePack-Doc:\n',
                           _msgpack.unpackb.__doc__))
