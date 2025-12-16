from typing import Callable
from PIL import Image

def open_img_with_func(
    img: Image.Image,
    func: Callable[[Image.Image], str]
):
    return func(img)
