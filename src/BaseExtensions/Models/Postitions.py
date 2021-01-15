from enum import IntEnum
from typing import *

from PIL.Image import Image

from .Json import *
from .Keys import Keys




__all__ = [
        'Ratios', 'Size', 'Point', 'CropBox', 'RotationAngle',
        ]

class RotationAngle(IntEnum):
    none = 0
    right = 90
    upside_down = 180
    left = 270

    def Rotate(self, angle: int = -90):
        return RotationAngle((self.value + angle) % 360)



class Size(BaseDictModel):
    __slots__ = []
    @property
    def width(self) -> int: return self.get(Keys.width)
    @property
    def height(self) -> int: return self.get(Keys.height)

    def ToTuple(self) -> Tuple[int, int]: return self.width, self.height

    @staticmethod
    def FromTuple(v: Tuple[int, int]): return Size.Create(*v)
    @classmethod
    def Create(cls, width: int, height: int): return cls({ Keys.width: width, Keys.height: height })

    @classmethod
    def Parse(cls, d):
        if d is None: return None
        if isinstance(d, dict):
            AssertKeys(d, Keys.width, Keys.height)
            return cls(d)

        throw(d, dict)
class Ratios(Size):
    @property
    def LANDSCAPE(self) -> float: return self.width / self.height
    @property
    def PORTRAIT(self) -> float: return self.height / self.width



class Point(BaseDictModel[str, int]):
    __slots__ = []
    @property
    def y(self) -> int: return self[Keys.y]
    @property
    def x(self) -> int: return self[Keys.x]

    def ToTuple(self) -> Tuple[int, int]: return self.x, self.y

    @staticmethod
    def FromTuple(v: Tuple[int, int]): return Point.Create(*v)
    @classmethod
    def Create(cls, x: int, y: int): return cls({ Keys.x: x, Keys.y: y })

    @classmethod
    def Parse(cls, d):
        if d is None: return None
        if isinstance(d, dict):
            AssertKeys(d, Keys.x, Keys.y)
            return cls(d)

        throw(d, dict)


class CropBox(BaseDictModel[str, int]):
    """  Adjusted box (x, y, width, height), ensuring that all dimensions resides within the boundaries. """
    __slots__ = []
    @property
    def y(self) -> int: return self[Keys.y]
    @property
    def x(self) -> int: return self[Keys.x]

    def Set(self, x: int, y: int):
        self[Keys.x] = x
        self[Keys.y] = y
        return self

    @property
    def width(self) -> int: return self.get(Keys.width)
    @property
    def height(self) -> int: return self.get(Keys.height)

    def Resize(self, width: int, height: int):
        self[Keys.width] = width
        self[Keys.height] = height
        return self

    def Update(self, pic: Point, img: Size, edit: Size) -> bool:
        """
            The goal is to find the area of the object that is visible, and return it's coordinates.

            x, y: root left point of the box, in (x, y) format.
            : bottom right point of the box, in (x, y) format.

        :param edit:
        :param pic:  root left point of the photo, in (x, y) format.
        :param img:  size of the photo, in (Width, Height) format.
        :return: True if all of the object will be visible, otherwise false.
        """
        if pic.x >= 0 and pic.y >= 0 and pic.y + img.height <= edit.height and pic.x + img.width <= edit.height: return True

        self[Keys.x] = 0 if pic.x > 0 else abs(self.x)


        def y(pic_y: int) -> int:
            if pic_y > 0:  return 0
            return abs(pic_y)
        self[Keys.y] = y(pic.y)


        def height(_y: int, _height: int, pic_y: int, img_h: int, edit_h: int) -> int:
            if pic_y + img_h >= edit_h: return edit_h + abs(pic_y)
            elif pic_y < 0 and _y + _height < edit_h: return img_h + pic_y

            return pic_y + img_h
        self[Keys.height] = height(self.y, self.height, pic.y, img.height, edit.height)


        def width(x: int, img_w: int, edit_w: int) -> int:
            if img_w + x > edit_w: return edit_w - x

            return img_w
        self[Keys.width] = width(self.x, img.width, edit.width)

        return False

    def MinScalingFactor(self, MaxWidth: int, MaxHeight: int) -> float: return min(MaxWidth / self.width, MaxHeight / self.height)
    def MaxScalingFactor(self, MaxWidth: int, MaxHeight: int) -> float: return max(MaxWidth / self.width, MaxHeight / self.height)

    @overload
    def EnforceBounds(self, image_size: Size) -> Tuple[int, int, int, int]: ...
    @overload
    def EnforceBounds(self, image_size: Image) -> Tuple[int, int, int, int]: ...
    @overload
    def EnforceBounds(self, image_size: Tuple[int, int]) -> Tuple[int, int, int, int]: ...

    def EnforceBounds(self, image_size: Union[Size, Image, Tuple[int, int]]) -> Tuple[int, int, int, int]:
        def convert(o) -> Tuple[int, int]:
            if isinstance(image_size, Size): return image_size.ToTuple()
            elif isinstance(image_size, Image): return image_size.size
            elif isinstance(image_size, tuple): return image_size
            throw(image_size, Size, Image, tuple)

        img_w, img_h = convert(image_size)
        return (
                self.x if self.x >= 0 else 0,
                self.y if self.y >= 0 else 0,
                self.width if self.width <= img_w else img_w,
                self.height if self.height <= img_h else img_h,
                )


    def Right(self, amount: int):
        self[Keys.x] += amount
        return self
    def Left(self, amount: int):
        self[Keys.x] -= amount
        return self
    def Up(self, amount: int):
        self[Keys.y] -= amount
        return self
    def Down(self, amount: int):
        self[Keys.y] += amount
        return self




    def ToTuple(self) -> Tuple[int, int, int, int]: return self.x, self.y, self.width, self.height
    def ToPointSize(self) -> Tuple[Point, Size]: return Point.Create(self.x, self.y), Size.Create(self.width, self.height)
    def ToPoints(self) -> Tuple[Point, Point]: return Point.Create(self.x, self.y), Point.Create(self.x + self.width, self.y + self.height)

    # noinspection PyMethodOverriding
    @classmethod
    def Create(cls, x: int, y: int, width: int, height: int):
        return cls({
                Keys.x:      x,
                Keys.y:      y,
                Keys.width:  width,
                Keys.height: height,
                })

    @classmethod
    def Crop(cls, x: int, y: int, width: int, height: int, *, pic: Point, img: Size, edit: Size):
        o = CropBox.Create(x, y, width, height)
        o.Update(pic, img, edit)
        return o

    @classmethod
    def FromPoints(cls, start: Point, end: Point):
        x1, y1 = start.ToTuple()
        x2, y2 = end.ToTuple()
        return CropBox.Create(x1, y1, x2 - x1, y2 - y1)

    @classmethod
    def FromPointSize(cls, start: Point, size: Size):
        x1, y1 = start.ToTuple()
        w, h = size.ToTuple()
        return CropBox.Create(x1, y1, w, h)

    @classmethod
    def BoxSize(cls, start: Point, end: Point, pic_pos: Point, img_size: Size):
        """
        :param start: root start point of the box, in (x, y) format.
        :param end: root end point of the box, in (x, y) format.
        :param pic_pos:  root left point of the photo, in (x, y) format.
        :param img_size:  size of the photo, in (width, height) format.
        :return: adjusted box dimensions, ensuring that it resides within the photo.
        """
        px, py = pic_pos.ToTuple()
        pw, ph = img_size.ToTuple()

        x1, y1 = start.ToTuple()
        x2, y2 = end.ToTuple()

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

        print(dict(x1=x1, y1=y1, x2=x2, y2=y2))
        return CropBox.Create(int(x1), int(y1), int(x2 - x1), int(y2 - y1))

    @classmethod
    def Parse(cls, d):
        if isinstance(d, dict):
            AssertKeys(d, Keys.width, Keys.height, Keys.x, Keys.y)
            return cls(d)

        throw(d, dict)
