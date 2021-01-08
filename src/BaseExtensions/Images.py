import os
from typing import overload

from PIL import Image




__all__ = [
        'ResizePhoto', 'IsImage'
        ]
def ResizePhoto(image: Image.Image, *, WidthMax: int or float, HeightMax: int or float) -> Image:
    scalingFactor = min((WidthMax / image.width, HeightMax / image.height))
    newSize = (int(scalingFactor * image.width), int(scalingFactor * image.height))
    return image.resize(newSize)



@overload
def IsImage(path: str) -> bool: ...
@overload
def IsImage(directory: str, fileName: str) -> bool: ...

def IsImage(path: str = None, directory: str = None, fileName: str = None, ) -> bool:
    try:
        if directory and fileName: path = os.path.join(directory, fileName)

        assert (os.path.isfile(path))
        with open(path, 'rb') as f:
            with Image.open(f) as img:
                assert (isinstance(img, Image.Image))
                img.verify()
                return True

    except (FileNotFoundError, ValueError, EOFError, Image.UnidentifiedImageError, Image.DecompressionBombError):
        return False
