import io
import PIL as pil
import torch
import numpy as np

def make_gif(images: list[pil.Image]) -> io.BytesIO:
    bytes = io.BytesIO()
    images[0].save(bytes, format='GIF', save_all=True, optimize=True, append_images=images[1:], loop=1, duration=300)
    bytes.name = 'image.gif'
    bytes.seek(0)
    return bytes

def img2bytes(img: pil.Image) -> io.BytesIO:
    bytes = io.BytesIO()
    img.save(bytes, 'JPEG')
    bytes.seek(0)
    return bytes
