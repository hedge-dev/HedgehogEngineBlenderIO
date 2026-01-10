from ctypes import Structure

class FieldsFromTypeHints(type(Structure)):
    def __new__(cls, name, bases, namespace):
        from typing import get_type_hints
        class AnnotationDummy:
            __annotations__ = namespace.get('__annotations__', {})
        annotations = get_type_hints(AnnotationDummy)
        namespace['_fields_'] = list(annotations.items())
        return type(Structure).__new__(cls, name, bases, namespace)