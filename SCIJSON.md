SciJSON serialize common scientific data types to json and back to original data types
===========

An initial python implementation -- in dev status.

This module implements a JSON encoder and decoder supporting addittional
types often used in scientific computations or engineering.
So it can be used to serialize data to JSON files for example.
All supported types can be serialized to valid JSON and can be
deserialized to the original types in python.

The main goals of this module are to provide easy extensability, to
keep human readability and to be elegant as possible:
For supporting a scustom type, only a tuple with some definitions must
be appended to the `TYPE_CODER_LIST`.
Such a tuple contains definitions for the serialization to valid JSON types
and for deserialziation to the origin types. For serialization, the tuple contains
the type identifier of the python type followed by a function that, converts the
python object to valid JSON types. The subsequent field is the type identifier in
the JSON domain. The last field contains the deserialization function, returning
the native python object.

In the JSON domain a type defined by this module will allways be inside a
JSON-Object with following schema:
```
{__type__: ['typename', [<serialized data>]]}
```
Example
---------
``` python
In [1026]: data = np.random.randn(2, 2)

In [1027]: s = SciJSONEncoder().encode(data)
In [1028]: s
Out[1028]: '{"__type__": ["ndarray", ["float64", [2, 2],
[-0.6035334921252804, -0.9812241692131949, -0.41874824665336285, -1.8832546212025774]]]}'
In [1029]: decoded = SciJSONDecoder().decode(s)
In [1030]: decoded
Out[1032]:
array([[-0.60353349, -0.98122417],
       [-0.41874825, -1.88325462]])

In [1033]: decoded == data
Out[1033]:
array([[ True,  True],
       [ True,  True]], dtype=bool)
```

Notes
-----
Be aware of floating point precision in JSON, if you need exactly the same bytes
as jour original object, this could be a problem!

TODO:
Check out further data types to be implemented
Maybe add support for usage of messagepack to store data binary -- another module to try, the best would be to have both supporting the same data types.

