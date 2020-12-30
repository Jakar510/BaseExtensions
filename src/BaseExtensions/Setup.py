import importlib
from typing import List




__all__ = ['ReadFromFile', 'ReadLinesFromFile', 'GetRequirements', 'GetVersion']


def ReadLinesFromFile(path: str) -> List[str]:
    with open(path, "r") as f:
        return f.readlines()

def ReadFromFile(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def GetVersion(o) -> str:
    if hasattr(o, '__version__'): return o.__version__
    elif hasattr(o, 'version'): return o.version
    elif hasattr(o, 'Version'): return o.Version
    elif hasattr(o, 'VERSION'): return o.VERSION
    else: raise AttributeError(f"can't get version from {o}")


def GetRequirements(path: str) -> List[str]:
    install_requires = []
    for line in ReadLinesFromFile(path):
        line = line.strip('\n')
        if line == 'pillow': package = importlib.import_module('PIL')
        else: package = importlib.import_module(line)
        VERSION = GetVersion(package)
        if VERSION.__class__.__name__ == 'module': VERSION = GetVersion(VERSION)

        install_requires.append(f'{line}>={VERSION}')
    return install_requires
