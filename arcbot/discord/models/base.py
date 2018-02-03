"""
    Description:
        Base classes to quickly derive other objects coming from JSON

    Contributors:
        - Patrick Hennessy
"""

from typing import List, Generic, TypeVar
from enum import Enum
from datetime import datetime

class Snowflake(int):
    pass

class DiscordObject(object):
    """
        Base class that allows for easy generation of Discord-specific objects
        - Recursively adds properties to classes based on their definition
        - If data has extra keys, the value is skipped
        - If the class has properties that data doesnt, it is set to None

        Adds a standardized and useful repr
    """
    def __new__(cls, *args, **kwargs):
        if not getattr(cls, "__instances__", False):
            setattr(cls, "__instances__", [])

        if not getattr(cls, "__slots__", False):
            setattr(cls, "__slots__", cls.__annotations__.keys())

        return super().__new__(cls)

    @classmethod
    def find(cls, query):
        for key, value in query.items():
            for instance in cls.__instances__:
                attr = getattr(instance, key)
                attr_type = type(attr)

                if issubclass(attr_type, (int, bool, str, float)):
                    if attr == attr_type(value):
                        return instance

    @classmethod
    def from_json(cls, data):
        new_obj = cls()
        new_obj.__raw_data__ = data

        # Iterate through properites in the class definition
        for property, typ in cls.__annotations__.items():
            if not data.get(property, None):
                default = getattr(new_obj, property, None)
                setattr(new_obj, property, default)
                continue

            elif issubclass(typ, datetime):
                fmt = '%Y-%m-%dT%H:%M:%S.%f'
                item = data.get(property)
                item = item.rsplit("+")[0]
                item = item.rsplit("Z")[0]
                new = datetime.strptime(item, fmt)
                setattr(new_obj, property, new)
                continue

            elif issubclass(typ, DiscordObject):
                item = data.get(property)
                new = typ.from_json(item)
                setattr(new_obj, property, new)
                continue

            elif issubclass(typ, list):
                new_list = getattr(new_obj, property, [])
                subtype = typ.__args__[0]

                for item in data.get(property, []):
                    if issubclass(subtype, DiscordObject):
                        new = subtype.from_json(item)
                    else:
                        new = subtype(item)
                    new_list.append(new)
                setattr(new_obj, property, new_list)
                continue

            else:
                setattr(new_obj, property, typ(data[property]))
                continue

        new_obj.__instances__.append(new_obj)
        return new_obj

    def update(self, data):
        for property, typ in self.__annotations__.items():
            if not data.get(property, None):
                continue

            elif issubclass(typ, datetime):
                fmt = '%Y-%m-%dT%H:%M:%S.%f'
                item = data.get(property)
                item = item.rsplit("+")[0]
                item = item.rsplit("Z")[0]
                new = datetime.strptime(item, fmt)
                setattr(self, property, new)
                continue

            else:
                setattr(self, property, typ(data[property]))
                continue

    def __repr__(self):
        classname = f"{type(self).__name__}"
        items = []

        for key in ["name", "username", "id"]:
            value = getattr(self, key, None)
            if value:
                items.append(f"\"{str(value)}\"")

        return "{}({})".format(classname, ", ".join(items))

class DiscordEnum(Enum):
    """
        Enum subclass that sets a default repr
    """
    def __repr__(self):
        classname = f"{type(self).__name__}"
        return f"{classname}.{self.name}({self.value})"
