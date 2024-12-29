from typing import Union, Iterable
import os
import json
from ...exceptions import HEIODevException


JSON_VALUE = Union[None, int, str, 'JSONWrapper']


class HEIOJSONException(HEIODevException):

    json_data: 'JSONWrapper'

    def __init__(self, message: str, json_data: 'JSONWrapper', *args: object):
        self.json_data = json_data
        super().__init__(message, *args)

    def get_json_path(self):
        path = ""

        json_data = self.json_data
        while json_data is not None:
            if isinstance(json_data.identifier, int):
                path = f"[{json_data.identifier}]" + path
            else:
                path = f"/{json_data.identifier}" + path

            json_data = json_data.parent

        return path


class JSONWrapper:

    parent: Union['JSONWrapper', None]

    identifier: str | int
    data: dict[str, JSON_VALUE] | list[JSON_VALUE]

    def __init__(self, identifier: str | int, data: dict[str, JSON_VALUE] | list[JSON_VALUE], parent: Union['JSONWrapper', None]):
        self.identifier = identifier
        self.parent = parent
        self.data = data

    def __getitem__(self, identifier: str | int):
        if isinstance(self.data, dict):
            if not isinstance(identifier, str):
                raise HEIOJSONException(f"Identifier has to be a string", self)

            if identifier not in self.data:
                raise HEIOJSONException(
                    f"Data has no property \"{identifier}\"", self)

        elif not isinstance(identifier, int):
            raise HEIOJSONException(f"Identifier has to be an integer", self)

        return self.data[identifier]

    def __contains__(self, item):
        return self.data.__contains__(item)

    def __iter__(self):
        if isinstance(self.data, dict):
            return self.data.items().__iter__()
        else:
            return self.data.__iter__()

    def get_property_fallback(self, identifier: str | int, fallback: JSON_VALUE = None):
        if identifier in self.data:
            return self.data[identifier]
        return fallback

    def parse(self, type, **kwargs):
        if not hasattr(type, "parse_json_data"):
            raise HEIOJSONException(
                f"Type \"{type.__name__}\" has no \"parse_json_data\" function", self)

        return type.parse_json_data(self, **kwargs)

    def parse_property(self, property: str, type, mandatory: bool = True, **kwargs: object):
        if not hasattr(type, "parse_json_data"):
            raise HEIOJSONException(
                f"Type \"{type.__name__}\" has no \"parse_json_data\" function", self)

        if property not in self.data:
            if mandatory:
                raise HEIOJSONException(
                    f"Data has no property \"{type}\"", self)
            else:
                return None

        return type.parse_json_data(self.data[property], **kwargs)

    @staticmethod
    def _wrap_data(identifier, json_data, parent):

        if isinstance(json_data, dict):
            data = {}
            result = JSONWrapper(identifier, data, parent)
            for key, value in json_data.items():
                data[key] = JSONWrapper._wrap_data(key, value, result)
            return result

        elif isinstance(json_data, list):
            data = []
            result = JSONWrapper(identifier, data, parent)
            for i, value in enumerate(json_data):
                data.append(JSONWrapper._wrap_data(i, value, result))
            return result

        return json_data

    @staticmethod
    def read_file(filepath: str):
        with open(filepath, "r") as file:
            data = json.load(file)

        filename = os.path.basename(filepath)
        return JSONWrapper._wrap_data(filename, data, None)
