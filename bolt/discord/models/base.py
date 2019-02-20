"""
    Description:
        Base classes to quickly derive other objects coming from JSON

    Contributors:
        - Patrick Hennessy
"""

import enum
from datetime import datetime

# Exceptions
class ModelMissingRequiredKeyError(Exception):
    pass


class ModelValidationError(Exception):
    pass


class ImmutableFieldError(Exception):
    pass


class Model(object):
    """
        Base class for data bound objects
        Allows consumers to instaniate new instances from json (marshaling)
        Able to serialize back to json from it's object format
        __repr_keys__ allows consumers to designate what the repr will print out
    """
    __repr_keys__ = []
    __immutable_fields__ = []

    @classmethod
    def marshal(cls, data):
        """
            Create a new instance of the class from the JSON data passed in
        """
        new_obj = cls()
        new_obj.__fields__ = {}
        new_obj.__immutable_fields__ = []

        for field_name, field in cls.__dict__.items():
            if not isinstance(field, Field):
                continue

            new_obj.__fields__[field_name] = field

            json_key = field.json_key if field.json_key else field_name
            json_data = data.get(json_key, None)

            if json_data is None and field.required:
                raise ModelMissingRequiredKeyError(f"{cls.__name__} model is missing required key {json_key}")
            elif json_data is None:
                setattr(new_obj, field_name, field.default)
            else:
                attr = field.marshal(json_data)
                setattr(new_obj, field_name, attr)

            if field.immutable:
                new_obj.__immutable_fields__.append(field_name)

        return new_obj

    def remarshal(self, data):
        """
            Apply updates to existing fields given JSON data
            Fails if an update comes to an immutable field
        """
        for field_name, field in self.__fields__.items():
            if not isinstance(field, Field):
                continue

            json_key = field.json_key if field.json_key else field_name

            if not json_key in data.keys():
                continue

            json_data = data[json_key]
            attr = field.marshal(json_data)

            if field.immutable and not getattr(self, field_name) == attr:
                raise ImmutableFieldError(f"Field {field_name} cannot be updated")

            setattr(self, field_name, attr)


    def serialize(self):
        """
            Turn object back into a JSON-ified object
        """
        dct = {}

        for item, field in self.__fields__.items():
            attr = getattr(self, item)
            key = field.json_key if field.json_key != item and field.json_key is not None else item

            if isinstance(attr, Model):
                dct[key] = attr.serialize()
            elif isinstance(attr, Enum):
                dct[key] = attr.value
            elif isinstance(attr, list):
                dct[key] = []
                for child in attr:
                    if isinstance(child, Model):
                        dct[key].append(child.serialize())
                    elif isinstance(child, Enum):
                        dct[key].append(child.value)
                    else:
                        dct[key].append(child)
            else:
                dct[key] = attr

        return dct

    def __repr__(self):
        """
            Pretty repr that allows models to specify keys to use
        """
        classname = f"{type(self).__name__}"
        items = []

        for key in self.__repr_keys__:
            value = str(getattr(self, key))
            items.append(f"{key}=\"{value}\"")

        if len(items) > 0:
            return "{}({})".format(classname, ", ".join(items))
        else:
            return "{}()".format(classname)

    def __setattr__(self, name, value):
        if name in self.__immutable_fields__:
            raise ImmutableFieldError(f"Field \"{name}\" is immutable, cannot be changed")
        else:
            return object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self.__immutable_fields__:
            raise ImmutableFieldError(f"Field \"{name}\" is immutable, cannot be deleted")
        else:
            return object.__delattr__(self, name)


class Field(object):
    """
        Conterpart class for Models, instructing the model how to consume json data
        Includes a nice repr
    """
    def __init__(self, typ, default=None, required=False, json_key=None, max_length=-1, immutable=False, nullable=True):
        self.type = typ
        self.default = default
        self.required = required
        self.json_key = json_key
        self.max_length = max_length
        self.immutable = immutable
        self.nullable = nullable

    def __repr__(self):
        if self.required is True:
            return f"Field({self.type.__name__}, required=True)"
        else:
            return f"Field({self.type.__name__})"

    def marshal(self, data):
        # Recursively marshal types of other models
        if issubclass(self.type, Model):
            return self.type.marshal(data)
        else:
            # Check if data is able to be None type
            if data is None:
                if self.nullable is True:
                    return None
                else:
                    raise ModelValidationError(f"Field cannot be nullified")

            # Cast it to intended type
            value = self.type(data)

            # Validate field
            if not self.max_length == -1 and len(value) > self.max_length:
                raise ModelValidationError("Length of input is too long")

            return value


class ListField(Field):
    """
        Subclass of Field that allows one to create a list of some primitive
    """
    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        self.default = kwargs.get('default', [])

    def marshal(self, data):
        if not self.max_length == -1 and len(data) > self.max_length:
            raise ModelValidationError("Length of input is too long")

        if not isinstance(data, list):
            raise ModelValidationError("Input data is not of type list")

        ret_list = []
        for item in data:
            if issubclass(self.type, Model):
                ret_list.append(self.type.marshal(item))
            else:
                ret_list.append(self.type(item))

        return ret_list


class Enum(enum.Enum):
    """
        A nice repr for enums
    """
    def __repr__(self):
        return f"{self.__class__.__name__}.{self._name_}"
        

class Snowflake(str):
    def __init__(self, value):
        if value and isinstance(value, str):
            value = int(value)

        self.timestamp = int(((value >> 22) + 1420070400000) / 1000)
        self.internal_worker_id = (value & 0x3E0000) >> 17
        self.internal_process_id = (value & 0x1F000) >> 12
        self.increment = value & 0xFFF
        self.value = value

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return self.value

    def __repr__(self):
        return str(self.value)

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.timestamp)


class Timestamp():
    def __init__(self, iso_date):
        fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
        iso_date = "".join(iso_date.rsplit(":", 1))
        self.datetime = datetime.strptime(iso_date, fmt)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.timestamp})"

    @property
    def timestamp(self):
        return int(self.datetime.timestamp())

# class Autoslots(type):
#     def __new__(metaclass, name, bases, dct):
#         slots = []
#
#         # Add fields to slots
#         for property, field in dct.items():
#             if isinstance(field, Field):
#                 slots.append(property)
#
#         # Merge items from predefined slots
#         if not dct.get('__slots__'):
#             dct['__slots__'] = set(slots)
#         else:
#             dct['__slots__'] = set(dct['__slots__'] + slots)
#
#         if not dct['__slots__']:
#             del dct['__slots__']
#
#         return super(Autoslots, metaclass).__new__(metaclass, name, bases, dct)
#
# class SearchableList(list):
#     """
#         Subclass of List that allows for Mongo-esque querying of contents
#         Example:
#             users.find_one({"id": "1234"})
#             users.find({"bot": False})
#     """
#     def find(self, query={}):
#         for instance in self.__iter__():
#             match = False
#             for key, value in query.items():
#                 attr = getattr(instance, key, None)
#                 attr_type = type(attr)
#
#                 if issubclass(attr_type, (int, bool, str, float)):
#                     match = (attr == attr_type(value))
#
#             if match:
#                 yield instance
#
#     def find_one(self, query={}):
#         for instance in self.__iter__():
#             if query == {}:
#                 return instance
#
#             match = False
#
#             for key, value in query.items():
#                 attr = getattr(instance, key, None)
#                 attr_type = type(attr)
#
#                 if issubclass(attr_type, (int, bool, str, float)):
#                     match = (attr == attr_type(value))
#
#             if match:
#                 return instance
