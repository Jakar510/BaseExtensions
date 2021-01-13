import base64

from PIL import Image as _Image, ImageFile, ImageTk

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


class Image(object):
    __slots__ = ['_img', '_path', '_fp', '_MaxWidth', '_MaxHeight']
    _path: Union[str, Path]
    _fp: Optional[BinaryIO]
    _img: _Image.Image
    _MaxWidth: Optional[int]
    _MaxHeight: Optional[int]
    def __init__(self, img: Optional[_Image.Image], MaxWidth: Optional[int], MaxHeight: Optional[int], *, LOAD_TRUNCATED_IMAGES: bool = True):
        self._img = img
        self._MaxWidth = MaxHeight
        self._MaxHeight = MaxWidth
        if MaxHeight and MaxWidth: self.Resize(check_metadata=True)
        ImageFile.LOAD_TRUNCATED_IMAGES = LOAD_TRUNCATED_IMAGES

    def __enter__(self):
        self._fp = open(self._path, 'wb')
        self._img = _Image.open(self._fp)
        return self
    def __exit__(self, *args):
        # exc_type, exc_val, exc_tb = args
        if self._fp and all(arg is None for arg in args): self.save()

        if self._fp:
            self._img.close()
            self._fp.close()
            self._fp = None
    def __call__(self, path: Union[str, Path]):
        self._path = path
        return self
    def save(self): self._img.save(self._fp)

    @property
    def Image(self) -> _Image.Image: return self._img

    def ToPhotoImage(self) -> ImageTk.PhotoImage: return ImageTk.PhotoImage(self._img)

    def _Maximum_ScalingFactor(self) -> float: return max(self._MaxWidth / self._img.width, self._MaxHeight / self._img.height)
    def _Minimum_ScalingFactor(self) -> float: return min(self._MaxWidth / self._img.width, self._MaxHeight / self._img.height)
    def _CalculateNewSize(self) -> Tuple[int, int]:
        scalingFactor = self._Minimum_ScalingFactor()
        return int(scalingFactor * self._img.width), int(scalingFactor * self._img.height)
    def _Scale(self, factor: float) -> Tuple[int, int]: return int(self._img.width * (factor or 1)), int(self._img.height * (factor or 1))


    def Rotate(self, *, angle: int = None, expand: bool = True, Offset: Tuple[int, int] = None, fill_color=None, center=None, resample=_Image.BICUBIC) -> Image:
        """
            CAUTION: Offset will TRIM the image if moved out of bounds of the image.

        :param fill_color:
        :param center:
        :param resample:
        :param Offset: int in range 0-360 angle to rotate
        :param angle:
        :param expand:
        :return:
        """
        if angle is None: return self._img
        return self._img.rotate(angle=angle, expand=expand, translate=Offset, fillcolor=fill_color, center=center, resample=resample)

    def Crop(self, box: CropBox) -> Image:
        self._img = self._img.crop(box.ToTuple())
        return self

    def CropZoom(self, box: CropBox, Scaled_Size: (int, int), *, reducing_gap=3.0) -> Image:
        self._img = self._img.resize(size=Scaled_Size, reducing_gap=reducing_gap)
        self._img = self.Crop(box)
        return self.Resize(reducing_gap=reducing_gap, check_metadata=False)

    def Zoom(self, factor: float, *, reducing_gap=3.0):
        self._img = self._img.resize(size=self._Scale(factor), reducing_gap=reducing_gap)
        return self

    def Resize(self, box: CropBox = None, *, check_metadata: bool, reducing_gap=3.0, resample=_Image.BICUBIC):
        if check_metadata:
            exif: _Image.Exif = self._img.getexif()
            if 'Orientation' in exif:  # check if image has exif metadata.
                if exif['Orientation'] == 3:
                    self._img = self._img.rotate(180, expand=True)
                elif exif['Orientation'] == 6:
                    self._img = self._img.rotate(270, expand=True)
                elif exif['Orientation'] == 8:
                    self._img = self._img.rotate(90, expand=True)

        self._img = self._img.resize(size=self._CalculateNewSize(), resample=resample, box=box.EnforceBounds(image_size=self._img.size), reducing_gap=reducing_gap)
        return self

    @classmethod
    def FromFile(cls, path: Union[str, Path], *, MaxWidth: int = None, MaxHeight: int = None) -> _Image.Image:
        Assert(path, str, Path)

        with open(path, 'rb') as f:
            with _Image.open(f) as img:
                return cls(img, MaxWidth, MaxHeight)

    @classmethod
    def FromBase64(cls, data: str, *, MaxWidth: int = None, MaxHeight: int = None):
        Assert(data, str)

        return Image.FromBytes(base64.b64decode(data), MaxWidth=MaxWidth, MaxHeight=MaxHeight)

    @classmethod
    def FromBytes(cls, data: bytes, *, MaxWidth: int = None, MaxHeight: int = None):
        Assert(data, bytes)

        with BytesIO(data) as buf:
            with _Image.open(buf) as img:
                return cls(img, MaxWidth, MaxHeight)



    @staticmethod
    @overload
    def IsImage(path: str, *file_types: str) -> bool: ...
    @staticmethod
    @overload
    def IsImage(path: Path, *file_types: str) -> bool: ...
    @staticmethod
    @overload
    def IsImage(path: bytes, *file_types: str) -> bool: ...

    @staticmethod
    def IsImage(path: Union[str, Path, bytes], *file_types: str) -> bool:
        if isinstance(path, Path): path = path.Value

        if isinstance(path, str):
            if not file_types: file_types = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG', '.tiff', '.bmp', '.gif', '.TIFF', '.BMP', '.GIF']
            if path.endswith(file_types):
                try:
                    with open(path, 'rb') as f:
                        with _Image.open(f) as img:
                            img.verify()
                            return True
                except (IOError, SyntaxError): return False

        elif isinstance(path, bytes):
            try:
                with BytesIO(path) as buf:
                    with _Image.open(buf) as img:
                        img.verify()
                        return True
            except (IOError, SyntaxError): return False

        return False

