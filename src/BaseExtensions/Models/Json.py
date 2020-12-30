import copy
from enum import Enum
from json import dumps, loads

from PythonDebugTools import *

from .MixIns import *




__all__ = [
        'BaseModel', 'BaseListModel', 'BaseDictModel', 'BaseSetModel', 'BaseDictNameIdItem'
        ]

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class BaseModel(object):
    @staticmethod
    def Assert(t: type, d: object):
        if not isinstance(d, t): BaseModel.throw(t, d)
    @staticmethod
    def throw(t: Union[Type, Tuple[Type, Type]], d: object): raise TypeError(f"""Expecting {t} got type {type(d)}  

{pp.getPPrintStr(d)}

""")
    @staticmethod
    def AssertKeys(d: dict, *args):
        try:
            for key in args: assert (key in d)
        except AssertionError as e:
            raise KeyError(f"Required keys {args} are missing.     existing keys: {d.keys()}") from e
    @staticmethod
    def ConvertBool(o) -> bool:
        if isinstance(o, bool): return o
        if isinstance(o, str): return o.lower() == 'true'

        BaseModel.throw(bool, o)
    @staticmethod
    def RaiseKeyError(key, d):
        assert (isinstance(d, dict))
        if hasattr(d, 'ToDict'):
            PrettyPrint(d.ToDict())
        else:
            PrettyPrint(d)

        # pp.pformat(d)
        raise KeyError(f'{key} not in {d.keys()}')



    def Clone(self): return copy.deepcopy(self)
    def ToString(self) -> str:
        try:
            return f'<{self.__class__.__qualname__} Object() [ {self.ToJsonString()} ]'
        except AttributeError:
            return f'<{self.__class__.__name__} Object() [ {self.ToJsonString()} ]'
    def _Filter(self, func: callable): raise NotImplementedError()
    def ToDict(self): raise NotImplementedError()
    def ToList(self): raise NotImplementedError()
    def enumerate(self): raise NotImplementedError()
    def Count(self) -> int: raise NotImplementedError()
    def Empty(self) -> bool: raise NotImplementedError()


    @classmethod
    def Parse(cls, d): return cls()
    @classmethod
    def FromJson(cls, string: Union[str, bytes, bytearray], **kwargs): return cls.Parse(loads(string, **kwargs))
    def ToJsonString(self) -> str: return dumps(self, indent=4, default=self.serialize)  # , cls=JsonEncoder)
    @staticmethod
    def serialize(o):
        if isinstance(o, Enum): return o.value

        if isinstance(o, BaseSetModel): return o.ToList()

        if isinstance(o, BaseListModel): return o

        if isinstance(o, BaseDictModel): return o.ToDict()

        if hasattr(o, 'ToList') and callable(o.ToList): return o.ToList()

        if hasattr(o, 'ToDict') and callable(o.ToDict): return o.ToDict()

        return o

class BaseListModel(list, BaseModel, List[_T]):
    def __init__(self, source: Union[List, Iterable] = None):
        super().__init__(source or [])
    def __str__(self): return self.ToString()

    def __contains__(self, item: _T): return super().__contains__(item)
    def __setitem__(self, key: int, value: _T): return super().__setitem__(key, value)
    def __getitem__(self, key: int) -> Optional[_T]:
        try: return super().__getitem__(key)
        except KeyError: return None
    def __iter__(self) -> Iterable[_T]: return super().__iter__()
    def enumerate(self) -> Iterable[Tuple[int, _T]]: return enumerate(self)

    @property
    def Count(self) -> int: return len(self)
    @property
    def Empty(self) -> bool: return self.Count == 0

    def Iter(self) -> Iterable[int]: return range(len(self))

    def _Filter(self, func: callable) -> List[_T]: return list(filter(func, self))
    def ToList(self) -> List[_T]: return list(self)


    def ToDict(self) -> Dict[int, _T]:
        d = { }
        for key, value in self.enumerate():
            if hasattr(value, 'ToDict') and callable(value.ToDict):
                d[key] = value.ToDict()
            else:
                d[key] = value
        return d


    @classmethod
    def Parse(cls, d):
        if isinstance(d, list):
            return cls(d)

        BaseModel.throw(list, d)

class BaseSetModel(set, BaseModel, Set[_T]):
    def __str__(self): return self.ToString()
    def __contains__(self, item: _T): return super().__contains__(item)
    def __delitem__(self, item: _T): return self.discard(item)
    # def __isub__(self, item: _T): return self.discard(item)
    def __iadd__(self, item: _T): return self.add(item)
    def __iter__(self) -> Iterable[_T]: return super().__iter__()
    def enumerate(self) -> Iterable[Tuple[int, _T]]: return enumerate(self)

    @property
    def Count(self) -> int: return len(self)
    @property
    def Empty(self) -> bool: return self.Count == 0

    def _Filter(self, func: callable): return filter(func, self)
    def extend(self, items: Union[List[_T], Set[_T]]):
        return self.update(items)
        # for _item in items: self.add(_item)

    def ToList(self) -> List[_T]: return [i for i in self]
    def ToDict(self) -> Dict[int, _T]: return dict(self.enumerate())

    @staticmethod
    def FromArgs(*items: _T): return BaseSetModel.Parse(items)

    @classmethod
    def Parse(cls, d):
        if isinstance(d, list):
            return cls(map(int, d))

        BaseModel.throw(list, d)

class BaseDictModel(dict, BaseModel, Dict[_KT, _VT]):
    def __init__(self, source: dict = None, **kwargs):
        if source is not None: super().__init__(source, **kwargs)
        else: super().__init__(**kwargs)
    def __str__(self): return self.ToString()

    def __delitem__(self, item: Union[_KT, _VT]): return super().__delitem__(item)
    def __contains__(self, item: Union[_KT, _VT]): return super().__contains__(item)
    def __setitem__(self, key: _KT, value: _VT): return super().__setitem__(key, value)
    def __getitem__(self, key: _KT) -> Optional[_VT]:
        try: return super().__getitem__(key)
        except KeyError: return None
    def __iter__(self) -> Iterable[_VT]: return super().__iter__()

    def values(self) -> Iterable[_VT]: return super().values()
    def items(self) -> Iterable[Tuple[_KT, _VT]]: return super().items()
    def keys(self) -> Iterable[_KT]: return super().keys()
    def enumerate(self) -> Iterable[Tuple[int, _T]]: return enumerate(self)

    @property
    def Count(self) -> int: return len(self)
    @property
    def Empty(self) -> bool: return self.Count == 0

    def _Filter(self, func: callable) -> List[_VT]: return list(filter(func, self.values()))

    def ToList(self) -> List[_T]: return list(self.items())



    def ToDict(self) -> Dict[_KT, Union[_VT, Dict, str]]:
        d = { }
        for key, value in self.items():
            if isinstance(value, Enum): d[key] = value.value

            elif isinstance(value, BaseListModel): d[key] = value

            elif isinstance(value, BaseSetModel): d[key] = value.ToList()

            elif isinstance(value, BaseDictModel): d[key] = value.ToDict()

            elif hasattr(value, 'ToList') and callable(value.ToDict): d[key] = value.ToList()

            elif hasattr(value, 'ToDict') and callable(value.ToDict): d[key] = value.ToDict()

            elif hasattr(value, 'ToString') and callable(value.ToString): d[key] = value.ToString()

            else: d[key] = value
        return d
    def ToJsonString(self) -> str: return dumps(self.ToDict(), indent=4, default=self.serialize)  # , cls=JsonEncoder)

    @classmethod
    def Parse(cls, d):
        if isinstance(d, dict):
            return cls(d)

        BaseModel.throw(dict, d)


    # def Iter(self) -> Iterable[int]:
    #     if 0 in self: return range(0, len(self))
    #     return range(1, len(self) + 1)

class BaseDictNameIdItem(BaseDictModel, IdMixin[str], NameMixin):
    def split(self) -> Tuple[str, str]: return self.ID, self.Name

    def test(self):
        _ = self.ID
