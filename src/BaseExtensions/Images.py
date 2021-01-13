import base64
import logging
from typing import *

from PIL import Image as _Image, ImageFile

from .Exceptions import ArgumentError
from .Models.Files import *
from .Models.Json import *
from .Models.Postitions import *




__all__ = [
        'ResizePhoto', 'IsImage'
        ]

def ResizePhoto(image: _Image.Image, *, WidthMax: int or float, HeightMax: int or float) -> _Image.Image:
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
            with _Image.open(f) as img:
                assert (isinstance(img, _Image.Image))
                img.verify()
                return True

    except (FileNotFoundError, ValueError, EOFError, _Image.UnidentifiedImageError, _Image.DecompressionBombError):
        return False


class Image(File):
    _img: _Image.Image
    def __init__(self, img: _Image.Image):
        self._img = img

    @property
    def Image(self) -> _Image.Image: return self._img



    def Resize(self, *, MaxWidth: int, MaxHeight: int, check_metadata: bool, box: Tuple[int, int, int, int] = None, reducing_gap=3.0,
               resample=_Image.BICUBIC) -> _Image.Image:
        if check_metadata:
            exif: _Image.Exif = self._img.getexif()
            if 'Orientation' in exif:  # check if image has exif metadata.
                if exif['Orientation'] == 3:
                    source = self._img.rotate(180, expand=True)
                elif exif['Orientation'] == 6:
                    source = self._img.rotate(270, expand=True)
                elif exif['Orientation'] == 8:
                    source = self._img.rotate(90, expand=True)

        newSize = CalculateNewSize(self._img.size, MaxWidth, MaxHeight)
        newBox = CropBox.EnforceBounds(box=box, image_size=self._img.size)

        try: self._img = self._img.resize(size=newSize, resample=resample, box=newBox, reducing_gap=reducing_gap)
        except Exception as e:
            raise ValueError(f"Image_Manipulator.Resize: {dict(newBox=newBox, box=box, image=self, newSize=newSize, MaxWidth=MaxWidth, MaxHeight=MaxHeight)}") from e

        return self

    @classmethod
    def FromFile(cls, path: Union[str, Path], *, MaxWidth: int = None, MaxHeight: int = None) -> _Image.Image:
        # if IsImage(path=path, logger=self._logger):
        with open(path, 'rb') as f:
            with _Image.open(f) as img:
                if MaxHeight and MaxWidth: return cls(img).Resize(MaxWidth=MaxWidth, MaxHeight=MaxHeight, check_metadata=True)
                return cls(img)

    @classmethod
    def FromBase64(cls, data: str, *, MaxWidth: int = None, MaxHeight: int = None):
        Assert(data, str)

        with io.BytesIO(base64.b64decode(data)) as buf:
            with _Image.open(buf) as img:
                if MaxHeight and MaxWidth: return cls(img).Resize(MaxWidth=MaxWidth, MaxHeight=MaxHeight, check_metadata=True)
                return cls(img)

    @classmethod
    def FromBytes(cls, data: bytes, *, MaxWidth: int = None, MaxHeight: int = None):
        Assert(data, bytes)

        with io.BytesIO(data) as buf:
            with _Image.open(buf) as img:
                if MaxHeight and MaxWidth: return cls(img).Resize(MaxWidth=MaxWidth, MaxHeight=MaxHeight, check_metadata=True)
                return cls(img)


ImageFile.LOAD_TRUNCATED_IMAGES = True


def Calculate_Maximum_ScalingFactor(size: Tuple[int, int], MaxWidth: int, MaxHeight: int) -> float:
    return max(MaxWidth / size[0], MaxHeight / size[1])
def Calculate_Minimum_ScalingFactor(size: Tuple[int, int], MaxWidth: int, MaxHeight: int) -> float:
    return min(MaxWidth / size[0], MaxHeight / size[1])
def CalculateNewSize(size: Tuple[int, int], MaxWidth: int, MaxHeight: int) -> Tuple[int, int]:
    oldWidth, oldHeight = size
    scalingFactor = Calculate_Minimum_ScalingFactor(size, MaxWidth, MaxHeight)
    return int(scalingFactor * oldWidth), int(scalingFactor * oldHeight)





def Scale(size: Tuple[Union[int, float], ...], factor: float) -> Tuple[int, ...]:
    if factor is None: factor = 1
    def multiply(num) -> int: return int(num * factor)
    return tuple(map(multiply, size))
# def IsImage(*, path: str = None, logger: logging.Logger,
#             file_types: tuple = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG', '.tiff', '.bmp', '.gif')) -> bool:
#     if path.endswith(file_types):
#         try:
#             with open(path, 'rb') as f:
#                 with Image.open(f) as img:
#                     img: Image.Image = img
#                     img.verify()
#                     return True
#
#         # except PermissionError: pass  # os.remove(path)
#         except (IOError, SyntaxError): pass
#         except Exception as e: logger.exception(e)
#
#     return False


def BoxSize(*, root_left: Tuple[int, int], x2: int, y2: int, pic_pos: Tuple[int, int], img_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
    """
    :param root_left: root left point of the box, in (x, y) format.
    :param x2: x compenent of bottom right point of the box.
    :param y2: y compenent of bottom right point of the box.
    :param pic_pos:  root left point of the photo, in (x, y) format.
    :param img_size:  size of the photo, in (width, height) format.
    :return: adjusted box dimensions, ensuring that it resides within the photo.
    """
    px, py = pic_pos
    pw, ph = img_size

    x1, y1 = root_left

    # going right
    x1 = x1 if x1 > px else px
    y1 = y1 if y1 > py else py

    # going left
    x1 = x1 if x1 < px + pw else px + pw
    y1 = y1 if y1 < py + ph else py + ph

    # going right
    x2 = x2 if x2 < px + pw else px + pw
    y2 = y2 if y2 < py + ph else py + ph

    # going left
    x2 = x2 if x2 > px else px
    y2 = y2 if y2 > py else py

    return int(x1), int(y1), int(x2), int(y2)

# def Box(*, x1: int, y1: int, width: int, hieght: int, pic_pos: Tuple[int, int], img_size: (int, int)) -> Tuple[int, int, int, int]:
#     """
#         root_left: root left point of the box, in (x, y) format.
#         bottom_right: bottom right point of the box, in (x, y) format.
#
#     :param x1: root_left X
#     :param y1: root_left Y
#     :param width: bottom_right X
#     :param hieght: bottom_right Y
#     :param pic_pos:  root left point of the photo, in (x, y) format.
#     :param img_size:  size of the photo, in (width, height) format.
#     :return: adjusted box dimensions, ensuring that it resides within the photo.
#     :return:
#     """
#     px, py = pic_pos
#     pw, ph = img_size
#
#     # going right
#     x1 = x1 if x1 > px else px
#     y1 = y1 if y1 > py else py
#     # going left
#     x1 = x1 if x1 < px + pw else px + pw
#     y1 = y1 if y1 < py + ph else py + ph
#
#     # going right
#     width = width if width < px + pw else px + pw
#     hieght = hieght if hieght < py + ph else py + ph
#     # going left
#     width = width if width > px else px
#     hieght = hieght if hieght > py else py
#
#     return int(x1), int(y1), int(width), int(hieght)


# def FullScaleCrop(*,
#                   root_left: Tuple[int, int] = None,
#                   bottom_right: Tuple[int, int] = None,
#                   x1: int = None, y1: int = None, x2: int = None, y2: int = None,
#                   box: Tuple[int, int, int, int] = None,
#                   pic_pos: Tuple[int, int],
#                   img_size: Tuple[int, int],
#                   edit_size: Tuple[int, int],
#                   original_image_size: Tuple[int, int],
#                   rotated: bool):
#     if root_left is not None:
#         x1, y1 = root_left
#     if bottom_right is not None:
#         x2, y2 = bottom_right
#     if box is not None:
#         x1, y1, x2, y2 = box
#
#     results = CropBox(x1=x1, y1=y1, x2=x2, y2=y2, pic_pos=pic_pos, img_size=img_size, edit_size=edit_size)
#     if results is ALL_IN: return None
#
#     return tuple(map(int, results))

# def CropBox(x1: int, y1: int, width: int, hieght: int, *, pic_pos: Tuple[int, int], img_size: Tuple[int, int], edit_size: (int, int)) -> Tuple[int, int, int, int] or None:
#     """
#         the goal is to find the area of the photo that is visible, and return it's coordinates.
#
#         root_left: root left point of the box, in (x, y) format.
#         bottom_right: bottom right point of the box, in (x, y) format.
#
#     :param edit_size:
#     :param x1: root_left X
#     :param y1: root_left Y
#     :param width: bottom_right X
#     :param hieght: bottom_right Y
#     :param pic_pos:  root left point of the photo, in (x, y) format.
#     :param img_size:  size of the photo, in (width, height) format.
#     :return: adjusted box dimensions, ensuring that it resides within the photo.
#     """
#     px, py = pic_pos
#     pw, ph = img_size
#     editW, editH = edit_size
#
#     if px >= 0 and py >= 0 and py + ph <= editH and px + pw <= editW:  # orange
#         return ALL_IN
#
#     # Y2
#     if py + ph >= editH:  # purple / green
#         hieght = editH + abs(py)
#     elif py < 0 and hieght < editH:  # red
#         hieght = ph + py
#     else:  # blues, pink,
#         hieght = py + ph
#
#     # Y1
#     if py > 0:  # 0 for [ blues, purple, pink, orange ]
#         y1 = 0
#     else:  # abs(y1) for [ red, green ]
#         y1 = abs(py)
#
#     # X2
#     if pw + x1 > editW:  # Dark blue
#         width = editW - x1
#     else:  # elif x2 > pw + x1:  # all but Dark Blue
#         width = pw
#
#     # X1
#     x1 = 0 if px > 0 else abs(x1)
#
#     return int(x1), int(y1), int(width), int(hieght)

# def Crop(*, root_left: Tuple[int, int], bottom_right: Tuple[int, int], pic_pos: Tuple[int, int], img_size: Tuple[int, int], edit_size: (int, int)) -> Tuple[int, int, int, int]:
#     """
#     :param edit_size:
#     :param root_left: root left point of the box, in (x, y) format.
#     :param bottom_right:  bottom right point of the box, in (x, y) format.
#     :param pic_pos:  root left point of the photo, in (x, y) format.
#     :param img_size:  size of the photo, in (width, height) format.
#     :return: adjusted box dimensions, ensuring that it resides within the photo.
#     """
#     x1, y1 = root_left
#     x2, y2 = bottom_right
#     return CropBox(x1=x1, y1=y1, x2=x2, y2=y2, pic_pos=pic_pos, img_size=img_size, edit_size=edit_size)


def load_image(path: Union[Path, str], width: int = None, height: int = None) -> _Image.Image:
    with open(path, 'rb') as f:
        with _Image.open(f) as img:
            return Resize(source=img, MaxWidth=width, MaxHeight=height, check_metadata=False)


# noinspection PyMethodMayBeStatic
class Image_Manipulator(object):
    """
        with img_resizer(path=os.path.join(IMAGE_DIRECTORY, file_name)) as resizer:
            resizer.save(rawData=file_data, MaxHeight=ScreenHeight, MaxWidth=ScreenWidth)
    """
    _path: str = ''
    def __init__(self, ScreenWidth: int or float, ScreenHeight: int or float, EditWidth: int or float, EditHeight: int or float, logger: logging.Logger):
        assert (ScreenWidth != ScreenHeight)
        assert (EditWidth != EditHeight)

        self._ScreenWidth = int(ScreenWidth)
        self._ScreenHeight = int(ScreenHeight)
        self.__EditWidth = int(EditWidth)
        self.__EditHeight = int(EditHeight)
        self._logger = logger
    def __enter__(self):
        self._fp = open(self._path, 'wb')
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fp.close()
        self._fp = None
    def __call__(self, path: str, *args, **kwargs):
        self._path = path
        return self
    def __str__(self) -> str: return self.ToString()
    def __repr__(self) -> str: return self.ToString()
    def ToString(self) -> str: return f"<{self.__class__.__name__}  Screen Size: ({self._ScreenHeight}x{self._ScreenHeight})>"


    def save(self, *, FileName: str = None, source: _Image.Image = None, Base64_data: str = None, rawData: bytes = None, MaxWidth: int = None, MaxHeight: int = None):
        self.Resize_Image(FileName=FileName, source=source, Base64_data=Base64_data, rawData=rawData, MaxWidth=MaxWidth, MaxHeight=MaxHeight).save(self._fp)

    def Resize(self, *, FileName: str = None, path: str = None, source: _Image.Image = None, Base64_data: str = None, rawData: bytes = None,
               MaxWidth: int = None, MaxHeight: int = None) -> _Image.Image:
        """

        :param path:
        :param rawData:
        :param Base64_data:
        :param FileName:
        :param source:
        :param MaxWidth:
        :param MaxHeight:
        :return:
        """
        if MaxHeight is None: MaxHeight = int(self._ScreenHeight)
        if MaxWidth is None: MaxWidth = int(self._ScreenWidth)

        if FileName:
            return self._read_from_image_file(path=path, resize=True, MaxWidth=MaxWidth, MaxHeight=MaxHeight)

        elif Path:
            return self._read_from_image_file(path=Path, resize=MaxHeight is not None and MaxWidth is not None, MaxWidth=MaxWidth, MaxHeight=MaxHeight)

        elif source:
            return Resize(source=source, MaxWidth=MaxWidth, MaxHeight=MaxHeight, check_metadata=False)

        elif Base64_data:
            return self._decode_base64_image(Base64Data=Base64_data, MaxWidth=MaxWidth, MaxHeight=MaxHeight)

        elif rawData:
            return self._decode_base64_image(rawData=rawData, MaxWidth=MaxWidth, MaxHeight=MaxHeight)

        else:
            raise ArgumentError('either FileName or SourceImage must be provided.')

    def Rotate(self, *, source: _Image.Image, angle: int = None, expand: bool = True, Offset: Tuple[int, int] = None, fill_color=None, center=None, resample=_Image.BICUBIC) -> _Image.Image:
        """
            CAUTION: Offset will TRIM the image if moved out of bounds of the image.

        :param fill_color:
        :param center:
        :param resample:
        :param source: original image
        :param Offset: int in range 0-360 angle to rotate
        :param angle:
        :param expand:
        :return:
        """
        if angle is None: return source
        return source.rotate(angle=angle, expand=expand, translate=Offset, fillcolor=fill_color, center=center, resample=resample)

    def Crop(self, *, source: _Image.Image, box: (int, int, int, int)) -> _Image.Image:
        """
        :param source:
        :param box: int: (left, upper, right, lower)
        :return:
        """
        assert (len(box) == 4 and all((isinstance(item, int) for item in box)))
        return source.crop(box=box)


    def CropZoom(self, *, source: _Image.Image, box: Tuple[int, int, int, int], reducing_gap=3.0, Scaled_Size: (int, int)) -> _Image.Image:
        # new = Resize(source=source, MaxHeight=self.__EditHeight, MaxWidth=self.__EditWidth, check_metadata=False, reducing_gap=reducing_gap)
        # new = Resize(source=source, MaxWidth=Scaled_Size[0], MaxHeight=Scaled_Size[1], check_metadata=False, reducing_gap=reducing_gap)
        new = source.resize(size=Scaled_Size, reducing_gap=reducing_gap)
        new = self.Crop(source=new, box=box)
        return Resize(source=new, MaxHeight=self._ScreenHeight, MaxWidth=self._ScreenWidth, reducing_gap=reducing_gap, check_metadata=False)


    def Zoom(self, *, source: _Image.Image, factor: float, reducing_gap=3.0):
        return source.resize(size=Scale(size=source.size, factor=factor), reducing_gap=reducing_gap)
