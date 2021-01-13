from enum import IntEnum
from typing import *

from .Json import *




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
    def width(self) -> int: return self.get('Width')
    @property
    def height(self) -> int: return self.get('Height')

    def ToTuple(self) -> Tuple[int, int]: return self.width, self.height

    @staticmethod
    def FromTuple(v: Tuple[int, int]): return Size.Create(*v)
    @classmethod
    def Create(cls, width: int, height: int):
        return cls({ 'Width': width, 'Height': height })


class Ratios(Size):
    @property
    def LANDSCAPE(self) -> float: return self.width / self.height
    @property
    def PORTRAIT(self) -> float: return self.height / self.width



class Point(BaseDictModel):
    __slots__ = []
    @property
    def y(self) -> int: return self['Y']
    @property
    def x(self) -> int: return self['X']

    def ToTuple(self) -> Tuple[int, int]: return self.x, self.y

    @staticmethod
    def FromTuple(v: Tuple[int, int]): return Point.Create(*v)
    @classmethod
    def Create(cls, x: int, y: int):
        return cls({ 'X': x, 'Y': y })



class CropBox(Point):
    """  Adjusted box (x, y, width, height), ensuring that all dimensions resides within the boundaries. """
    def ToTuple(self) -> Tuple[int, int, int, int]: return self.x, self.y, self.width, self.height
    def ToPointSize(self) -> Tuple[Point, Size]: return Point.Create(self.x, self.y), Size.Create(self.width, self.height)
    def ToPoints(self) -> Tuple[Point, Point]: return Point.Create(self.x, self.y), Point.Create(self.x + self.width, self.y + self.height)

    @property
    def width(self) -> int: return self.get('Width')
    @property
    def height(self) -> int: return self.get('Height')

    def Update(self, pic: Point, img: Size, edit: Size) -> bool:
        """
            the goal is to find the area of the photo that is visible, and return it's coordinates.

            root_left: root left point of the box, in (x, y) format.
            bottom_right: bottom right point of the box, in (x, y) format.

        :param edit:
        :param pic:  root left point of the photo, in (x, y) format.
        :param img:  size of the photo, in (Width, Height) format.
        :return: adjusted box dimensions, ensuring that it resides within the photo.
        """
        if pic.x >= 0 and pic.y >= 0 and pic.y + img.height <= edit.height and pic.x + img.width <= edit.height: return True

        # x
        self['x'] = 0 if pic.x > 0 else abs(self.x)


        def y(pic_y: int):
            if pic_y > 0:  return 0
            return abs(pic_y)
        self['y'] = y(pic.y)


        def height(pic_y: int, img_h: int, edit_h: int):
            if pic_y + img_h >= edit_h: return edit_h + abs(pic_y)
            elif pic_y < 0 and self.y + self.height < edit_h: return img_h + pic_y

            return pic_y + img_h
        self['Height'] = height(pic.y, img.height, edit.height)


        def width(x: int, img_w: int, edit_w: int):
            if img_w + x > edit_w: return edit_w - x

            return img_w
        self['Width'] = width(self.x, img.width, edit.width)

        return False

    def MinScalingFactor(self, MaxWidth: int, MaxHeight: int) -> float: return min(MaxWidth / self.width, MaxHeight / self.height)
    def MaxScalingFactor(self, MaxWidth: int, MaxHeight: int) -> float: return max(MaxWidth / self.width, MaxHeight / self.height)

    @overload
    def EnforceBounds(self, image_size: Size) -> Tuple[int, int, int, int]: ...
    @overload
    def EnforceBounds(self, image_size: Tuple[int, int]) -> Tuple[int, int, int, int]: ...

    def EnforceBounds(self, image_size: Union[Size, Tuple[int, int]]) -> Tuple[int, int, int, int]:
        # box: Optional[Tuple[int, int, int, int]]
        # if box is None: return 0, 0, image_size[0], image_size[1]
        x1, y1, x2, y2 = self.ToTuple()
        px, py = image_size.ToTuple() if isinstance(image_size, Size) else image_size
        return (
                x1 if x1 >= 0 else 0,
                y1 if y1 >= 0 else 0,
                x2 if x2 <= px else px,
                y2 if y2 <= py else py,
                )

    # noinspection PyMethodOverriding
    @classmethod
    def Create(cls, x: int, y: int, width: int, height: int):
        return cls({
                'X':      x,
                'Y':      y,
                'Width':  width,
                'Height': height,
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
