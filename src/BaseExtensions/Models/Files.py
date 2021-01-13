import io
import os
from os import PathLike
from os.path import *
from pathlib import Path as _Path
from typing import *




class Path(object, PathLike, _PathLike):
    def __init__(self, path: str):
        self._path = path

    @property
    def Exists(self) -> bool: return exists(self._path)

    @property
    def IsFile(self) -> bool: return isfile(self._path)
    @property
    def IsDirectory(self) -> bool: return isdir(self._path)
    @property
    def IsLink(self) -> bool: return islink(self._path)

    @property
    def BaseName(self) -> str: return basename(self._path)
    @property
    def DirectoryName(self) -> str: return dirname(self._path)

    @property
    def SizeOf(self) -> int: return getsize(self._path)

    @classmethod
    def Create(cls, path: str):
        return cls(os.path.abspath(path))
    @classmethod
    def FromPathLibPath(cls, path: _Path):
        return cls(os.path.abspath(path.resolve()))
    @classmethod
    def FromArgs(cls, *args: str):
        return cls(os.path.join(*args))


    def __str__(self): return self._path
    def __repr__(self): return f'<Path Object. Location: "{self._path}">'


    def __bytes__(self):
        """ Return the bytes representation of the path. This is only recommended to use under Unix. """
        return os.fsencode(self._path)

    def __fspath__(self): return self._path

    @property
    def Value(self): return self._path



class BaseFile(object):
    _fp: Union[io.BytesIO, io.StringIO, TextIO]
    def __init__(self, mode: str = None):
        self._mode = mode

    def Open(self, **kwargs): raise NotImplementedError()
    def Close(self): raise NotImplementedError()

    def __enter__(self, **kwargs): return self.Open()
    def __exit__(self, exc_type, exc_val, exc_tb): self.Close()
class LocalFile(BaseFile):
    _path: Path
    def __init__(self, path: Path, mode: str):
        super().__init__(mode)
        self._path = path

    def Open(self, **kwargs):
        self._fp = open(self._path.Value, self._mode, **kwargs)
        return self._fp
    def Close(self):
        if self._fp:
            self._fp.close()
            del self._fp

class VirtualFile(BaseFile):
    def Open(self, **kwargs):
        self._fp = io.BytesIO(**kwargs)
        return self._fp
    def Close(self):
        if self._fp:
            self._fp.close()
            del self._fp

