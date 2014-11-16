A format for serializing scientific data
===========

An initial python implementation -- in dev status.

This module implements type encoders an decoders to be used with msgpack and json to serialize data-types often used in scientific computations or engineering.
So it can be used to serialize data to MessagePack or JSON files for example.
All supported types can be serialized and can be
deserialized to the original types in python. If a type is not supported, the option for enabling
pickle is given. But this pickle option is for python internal use only.

The main goals of this module are to provide easy extensability, to be verbose and to be elegant as possible:
For supporting a custom type, only a class with the attributes `type_`, `typestr`, `encode` and `decode` must be implemented and an instance can be added to the `TYPE_CODER_LIST`.
Example of a coder to support serialization of propper datetime with timezone:
```python
class DateTimeCoder:
    from datetime import datetime  # import the type
    import dateutil.parser  # import the parser for decoding
    type_ = datetime  # defining the type in program domain
    typestr = 'datetime'  # defining the type in the serialized domain
    def encode(self, obj):  # function to encode serializable object
        return {'isostr': datetime.isoformat(obj)}
    def decode(self, data):  # function to decode serialized object to origin types
        return self.dateutil.parser.parse(data['isostr'])
```

A serialied example:

```
{"~_type_~": "datetime",
 "isostr": "2014-12-24T05:55:55.555+00"}
```

Example
-----
```python
from datetime import datetime
import numpy as np
data = [[datetime.today()], datetime.today()- datetime.today(), np.random.randn(3), {'Hallo'}]
out = encode_types(data, TYPE_CODER_LIST, enable_pickle=True)
res = decode_types(out, TYPE_CODER_LIST, enable_pickle=True)
    
out_msgpack = msgpack.packb(out, encoding='utf-8', use_bin_type=True)
res_msgpack = decode_types(msgpack.unpackb(out_msgpack, encoding='utf-8'), enable_pickle=True)
for d, r in zip(data, res_msgpack): print(d==r)

True
True
[ True  True  True]
True

In [454]: data
Out[454]: 
[[datetime.datetime(2014, 11, 16, 19, 28, 12, 93000)],
 datetime.timedelta(0),
 array([-0.56142362, -0.39822492,  1.17505221]),
 set(['Hallo'])]

In [455]: out
Out[455]: 
[[{'isostr': '2014-11-16T19:28:12.093000', '~_type_~': 'datetime'}],
 {'days': 0, 'microsec': 0, 'seconds': 0, '~_type_~': 'timedelta'},
 {'dtype': 'float64',
  'shape': [3L],
  'valuebytes': '\xd1[\xe9\xaa.\xf7\xe1\xbf{\xb6\x86`\x84|\xd9\xbf\xe7\xbcM\x8c\x03\xcd\xf2?',
  '~_type_~': 'ndarray'},
 {'s': "c__builtin__\nset\np0\n((lp1\nS'Hallo'\np2\natp3\nRp4\n.",
  '~_type_~': 'pypickle'}]

In [456]: out_msgpack
Out[458]: "\x94\x91\x82\xc4\x06isostr\xc4\x1a2014-11-16T19:28:12.093000\xc4\x08~_type_~\xc4\x08datetime\x84\xc4\x07seconds\x00\xc4\x08microsec\x00\xc4\x04days\x00\xc4\x08~_type_~\xc4\ttimedelta\x84\xc4\x05dtype\xc4\x07float64\xc4\x05shape\x91\x03\xc4\nvaluebytes\xc4\x18\xd1[\xe9\xaa.\xf7\xe1\xbf{\xb6\x86`\x84|\xd9\xbf\xe7\xbcM\x8c\x03\xcd\xf2?\xc4\x08~_type_~\xc4\x07ndarray\x82\xc4\x01s\xc40c__builtin__\nset\np0\n((lp1\nS'Hallo'\np2\natp3\nRp4\n.\xc4\x08~_type_~\xc4\x08pypickle"

```

As you can see, strings are strings in  out_msgpack. If you only would like to use msgpack, there is support to add extensions to it. Then you could define a much shorter identifier. So there is potential for improovement on the idea. But one goal until now is to support both json AND msgpack and only defining the coders once. Mabe have a look at transits way and how they do it.

Notes
-----
Be aware of floating point precision in JSON, if you need exactly the same bytes
as jour original object, this could be a problem!

TODO:
Check out further data types to be implemented
Maybe add support for usage of messagepack to store data binary -- another module to try, the best would be to have both supporting the same data types.

