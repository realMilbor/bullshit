from datetime import datetime
from typing import *
from collections import OrderedDict
from Schema import Schema


class Model:
    pass


class MetaModel(type):
    def __new__(mcs, name: str, superclasses: Tuple[type, ...], namespace: dict, **kwds) -> type:
        schema = kwds.get('schema', Schema([]))

        def ivar_name(attribute_name: str) -> str:
            assert attribute_name and attribute_name.isidentifier(), "Attribute name must be an identifier: " + str(attribute_name)
            return '_' + attribute_name

        def make_property(prop: Schema.Property) -> property:
            ivar = ivar_name(prop.name)
            typeobj = prop.type
            is_nullable = prop.is_nullable

            def generated_get(self):
                return getattr(self, ivar, None)

            def generated_set(self, value: typeobj):
                assert is_nullable if value is None else isinstance(value, typeobj)
                setattr(self, ivar, value)

            def generated_del(self):
                delattr(self, ivar)

            docstring = "Autogenerated property '" + str(name) + "' of type " + str(typeobj)

            return property(generated_get, generated_set, generated_del, docstring)

        def generated_init(self, *args, **kwargs) -> None:
            ordered_arguments = list(args)
            for p in schema:
                if p.name in kwargs:
                    value = kwargs[p.name]
                else:
                    value = ordered_arguments.pop(0) if ordered_arguments else None

                assert prop.is_nullable if value is None else isinstance(value, p.type), "Property is not nullable: " + prop.name
                setattr(self, ivar_name(p.name), value)

        def generated_serialize(self) -> Tuple:
            result = OrderedDict()
            for key, value in [(p.name, getattr(self, ivar_name(p.name), None)) for p in schema]:
                result[key] = value
            return result

        def generated_str(self) -> str:
            identity = '<model "' + name + '" at ' + hex(id(self)) + '>'
            content = '{' + ', '.join([p.name + ': ' + str(getattr(self, ivar_name(p.name))) for p in schema]) + '}'
            return identity + ' ' + content

        for prop in schema:
            namespace[prop.name] = make_property(prop)

        namespace['__init__'] = generated_init
        namespace['__str__'] = generated_str
        namespace['serialize'] = generated_serialize
        namespace['schema'] = property(lambda self: schema, lambda self, value: None, lambda self: None, '''schema''')
        superclasses = (Model, *superclasses)
        return super(MetaModel, mcs).__new__(mcs, name, superclasses, namespace)

    @classmethod
    def create(mcs, name: str, schema: Schema) -> type:
        return mcs(name, (), {}, schema=schema)


class Car(metaclass=MetaModel, schema=Schema.car()):
    pass


class Service(metaclass=MetaModel, schema=Schema.service()):
    pass


class Master(metaclass=MetaModel, schema=Schema.master()):
    pass


class Work(metaclass=MetaModel, schema=Schema.work()):
    pass
