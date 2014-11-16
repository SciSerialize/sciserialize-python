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

Notes
-----
Be aware of floating point precision in JSON, if you need exactly the same bytes
as jour original object, this could be a problem!

TODO:
Check out further data types to be implemented
Maybe add support for usage of messagepack to store data binary -- another module to try, the best would be to have both supporting the same data types.

