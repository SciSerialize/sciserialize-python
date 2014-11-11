from json import JSONEncoder, JSONDecoder
from datetime import datetime, timedelta
import dateutil.parser
import numpy as np
from pandas import DataFrame as pandas_DataFrame
from pandas import read_json as pandas_read_json


"""This module implements a JSON encoder and decoder supporting addittional
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

{__type__: ['typename', [<serialized data>]]}

Example
-------
``` Python
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
Be aware of floating point precision in JSON, if jou need exactly the same bytes
as jour original object, this could be a problem!

"""

TYPE_KEY = '__type__'

### An Element of the `TYPE_CODER_LIST` is a
### tuple containing following definitions:
#   (
#       python-type,
#       function for serialization to json types,
#       json-type-string,
#       function for deserialization to python type
#   ),
#
#   the list can be extended based on the convention for valid JSON-types.
#
TYPE_CODER_LIST = [
    (
        datetime, # Type in Python.
        lambda obj: datetime.isoformat(obj),  # Serialization.
        'datetime',  # Name of the type in JSON.
        lambda data: dateutil.parser.parse(data)  # Deserialization.
    ),
    (
        timedelta,
        lambda obj:  (obj.days, obj.seconds, obj.microseconds),
        'timedelta',
        lambda data: timedelta(*data)
    ),
    (
        np.matrix,
        lambda obj: (str(obj.dtype), list(obj.shape), np.ravel(obj).tolist()),
        'matrix2d',
        lambda d: np.matrix(d[2], dtype=np.typeDict[d[0]]).reshape(d[1])
    ),
    (
        np.ndarray,
        lambda obj: (str(obj.dtype), list(obj.shape), np.ravel(obj).tolist()),
        'ndarray',
        lambda d: np.array(d[2], dtype=np.typeDict[d[0]]).reshape(d[1])
    ),
    (
        pandas_DataFrame,
        lambda obj: obj.to_json(double_precision=15),
        'pandas.DataFrame',
        lambda data: pandas_read_json(data)
    ),
]


### Encoder and Decoder definitions
# as far as possible only change the TYPE_CODER_LIST above!
# The remaining code should be generic (except of __main__-part).

class SciJSONEncoder(JSONEncoder):
    """Extended JSONEncoder with support of types defined in TYPE_CODER_LIST.
    Types are encoded to a valid json string and can be decoded
    with the SciJSONDecoder.
    """
    def __init__(self, type_coder_list=TYPE_CODER_LIST, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._type_coder_list = type_coder_list

    def default(self, obj):
        for type_, encode, jtype, decode in self._type_coder_list:
            if isinstance(obj, type_):
                return {TYPE_KEY : (jtype, encode(obj))}
        return JSONEncoder.default(self, obj)

class SciJSONDecoder(JSONDecoder):
    """Extended JSONDecoder with support of types defined in TYPE_CODER_LIST.
    Types are encoded to the vallid python types and can be encoded again
    with the SciJSONEncoder.
    """
    def __init__(self, type_coder_list=TYPE_CODER_LIST, *args, **kwargs):
        super(self.__class__, self).__init__(
            object_hook=self.dict_to_object, *args, **kwargs)
        self._type_coder_list = type_coder_list

    def dict_to_object(self, d):
        if TYPE_KEY not in d: return d
        data = d.pop(TYPE_KEY)
        type_ = data.pop(0)
        for dummy, encode, jtype, decode  in self._type_coder_list:
            if type_ == jtype:
                return decode(data[0])

        # if type was not declared return raw data:
        d[TYPE_KEY] = (type_, data)
        return d


if __name__ == '__main__':

    import pandas as pd
    from numpy.random import randn

    dp = pd.date_range(start='2014-08-22 10:30:45.1234',
                       end='2014-08-30 20:40', tz='UTC').to_pydatetime()
    dl = dp.tolist()
    dt = dl[1]-dl[-1]
    input_ = [dt,dl,dp,
           'Hallo',
           1.2788348,
           randn(3,9),
           np.matrix(randn(2,3)),
           pd.DataFrame(randn(2,3))]
    js = SciJSONEncoder().encode(input)
    decoded = SciJSONDecoder().decode(js)

    print(input_)
    print(decoded)

    ## Really, the most deserialzed datatypes are exactly the same compared
    ## the original objects:
    for i, d in zip(input_, decoded): print(i==d)

    ## As you can see the serialization of DataFrame is not totally precise.
    ## This is because the pandas json serialzer only allows a double_precision=15.
