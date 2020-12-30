import base64
import hashlib
import json
import os
import pickle




__all__ = [
        'GetFileData', 'GetHashID',
        ]

def GetFileData(path, load: callable, *, Default=None, Check: callable = None, RemoveOnError: bool = False):
    try:
        with open(path, 'rb') as f:
            dat = load(f)
            if Check: Check(dat)
            return dat
    except FileNotFoundError: return Default
    except (pickle.PickleError, pickle.PicklingError, json.JSONDecodeError):
        if RemoveOnError: os.remove(path)
        return Default

def GetHashID(file_path: str, BlockSize: int = 65536) -> str:
    """
    :param file_path: os.path string to the file.
    :param BlockSize: defaults to 64KB
    :return:
    """
    if os.path.isdir(file_path): raise IsADirectoryError('Argument cannot be a directory.')

    _hasher = hashlib.sha1()
    with open(file_path, 'rb') as f:
        buf = f.read(BlockSize)
        while len(buf) > 0:
            _hasher.update(buf)
            buf = f.read(BlockSize)
    return base64.urlsafe_b64encode(_hasher.digest()).decode()
