import os
from os import PathLike
from os.path import *
from pathlib import Path as _Path
from typing import Union




class Path(PathLike):
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
    def __repr__(self):
        try: return f'<{self.__class__.__qualname__} Object. Location: "{self._path}">'
        except AttributeError: return f'<{self.__class__.__name__} Object. Location: "{self._path}">'


    def __bytes__(self):
        """ Return the bytes representation of the path. This is only recommended to use under Unix. """
        return os.fsencode(self._path)

    def __fspath__(self): return self._path

    @property
    def Value(self): return self._path

    @staticmethod
    def CopyFile(_inPath: Union[str, 'Path'], _outPath: Union[str, 'Path'], open_as_binary: bool = False):
        with open(_outPath, 'wb' if open_as_binary else 'w') as out:
            with open(_inPath, 'rb' if open_as_binary else 'r') as _in:
                out.write(_in.read())

# _TFile = TypeVar("_TFile", BytesIO, StringIO, FileIO, TextIOWrapper)
# class FileMode(str, Enum):
#     """
#     ========= ===============================================================
#     Character Meaning
#     --------- ---------------------------------------------------------------
#     'r'       open for reading (default)
#     'w'       open for writing, truncating the file first
#     'x'       create a new file and open it for writing
#     'a'       open for writing, appending to the end of the file if it exists
#     'b'       binary mode
#     't'       text mode (default)
#     '+'       open a disk file for updating (reading and writing)
#     ========= ===============================================================
#     """
#     Text = 't'
#
#     Read = 'r'
#     Write = 'w'
#     Create = 'x'
#     Append = 'a'
#
#     ReadBytes = 'rb'
#     WriteBytes = 'wb'
#     CreateBytes = 'xb'
#     AppendBytes = 'ab'
#
#     ReadWrite = 'w+'
#     ReadWriteBytes = 'wb+'
#
#     @staticmethod
#     def IsBinary(o):
#         if isinstance(o, FileMode):
#             return o == FileMode.ReadBytes or o == FileMode.WriteBytes or o == FileMode.ReadWriteBytes or o == FileMode.AppendBytes or o == FileMode.CreateBytes
#
#         return False
#     @staticmethod
#     def IsText(o):
#         if isinstance(o, FileMode):
#             return o == FileMode.Text
#
#         return False
#     @staticmethod
#     def IsString(o):
#         if isinstance(o, FileMode):
#             return o == FileMode.Read or o == FileMode.Write or o == FileMode.ReadWrite or o == FileMode.Create or o == FileMode.Append
#
#         return False
#
#
#
# class BaseFile(Generic[_TFile]):
#     _fp: Optional[_TFile]
#     _mode: FileMode
#     def __init__(self, mode: FileMode): self._mode = mode
#
#     def __enter__(self, **kwargs): return self.Open()
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self._fp:
#             self._fp.__exit__(exc_type, exc_val, exc_tb)
#             self._fp = None
#
#     def Open(self, **kwargs):
#         self._fp.__enter__()
#         return self._fp
#
#     # def close(self) -> None: self._fp.close()
#     # def fileno(self) -> int: return self._fp.fileno()
#     # def flush(self) -> None: self._fp.flush()
#     # def isatty(self) -> bool: return self._fp.isatty()
#     # def tell(self) -> int: return self._fp.tell()
#     # def truncate(self, size: Optional[int] = -1) -> int: return self._fp.truncate(size)
#     # def seek(self, offset: int, whence: int = 0) -> int: return self._fp.seek(offset, whence)
#     # def seekable(self) -> bool: return self._fp.seekable()
#     #
#     # def read(self, n: int = -1) -> AnyStr: return self._fp.read(n)
#     # def readable(self) -> bool: return self._fp.readable()
#     # def readline(self, limit: int = -1) -> AnyStr: return self._fp.readline(limit)
#     # def readlines(self, hint: int = -1) -> list[AnyStr]: return self._fp.readlines(hint)
#     #
#     # def writable(self) -> bool: return self._fp.writable()
#     # def write(self, s: AnyStr) -> int: return self._fp.write(s)
#     # def writelines(self, lines: Iterable[AnyStr]) -> None: return self._fp.writelines(lines)
#     #
#     # def __next__(self) -> AnyStr: return self._fp.__next__()
#     # def __iter__(self) -> Iterator[AnyStr]: return self._fp.__iter__()
#
#
# class LocalFile(BaseFile):
#     _path: Path
#     def __init__(self, path: Path, mode: FileMode):
#         super().__init__(mode)
#         self._path = path
#
#     def Open(self, **kwargs):
#         self._fp = open(self._path.Value, self._mode.value, **kwargs)
#         return super().Open()
#
#
# class VirtualFile(BaseFile[_TFile]):
#     def Open(self, *args, **kwargs):
#         if FileMode.IsBinary(self._mode):
#             self._fp = BytesIO(*args, **kwargs)
#
#         if FileMode.IsString(self._mode):
#             self._fp = StringIO(*args, **kwargs)
#
#         if FileMode.IsText(self._mode):
#             self._fp = TextIOWrapper(*args, **kwargs)
#
#         return super().Open()

