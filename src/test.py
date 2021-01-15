import json
import time

from BaseExtensions.Models import *
from src.BaseExtensions.Images import ImageObject




def Test():
    pass
    # from TkinterExtensions.examples import run_all
    # run_all()

    # with open('test.txt', 'a+') as f: f.write(f.read())

    start = Point.Create(0, 0)
    end = Point.Create(150, 150)
    pic_pos = Point.Create(10, 10)
    img_size = Size.Create(200, 200)

    print(CropBox.BoxSize(start, end, pic_pos, img_size))

    t = (1, 2)
    print(json.dumps(img_size))

    with open('./BaseExtensions/ImageExtensions.py', 'w') as f:
        f.write('from enum import Enum\n')
        f.write('\n')
        f.write('\n')
        f.write('\n')
        f.write('class ImageExtensions(str, Enum):\n')

        for item in ImageObject.Extensions():
            f.write(f"\t{item.replace('.', '')} = '{item}'\n")




if __name__ == '__main__':
    Test()
