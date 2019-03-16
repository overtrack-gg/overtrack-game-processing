from pynamodb.attributes import ListAttribute


class TupleAttribute(ListAttribute):
    def __init__(self, length=None, hash_key=False, range_key=False, null=None, default=None, attr_name=None):
        super(TupleAttribute, self).__init__(hash_key=hash_key,
                                             range_key=range_key,
                                             null=null,
                                             default=default,
                                             attr_name=attr_name)
        self.length = length
        if self.default is not None and not isinstance(self.default, tuple):
            raise TypeError('Default value must be a tuple')

    def serialize(self, values):
        if self.length is not None and len(values) != self.length:
            raise TypeError('Expected tuple of length %d but had %d' % (self.length, len(values)))
        return super(TupleAttribute, self).serialize(values)

    def deserialize(self, value):
        if value is None:
            if self.null:
                return self.default
            else:
                raise TypeError('Got None but null=False')
        else:
            result = super(TupleAttribute, self).deserialize(value)
            if self.length is not None and len(result) != self.length:
                raise TypeError('Expected tuple of length %d but had %d' % (self.length, len(result)))
            return tuple(result)
