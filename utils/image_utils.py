# image_utils.py - generated file


import os
from PIL import Image

def is_image_file(filepath):
    """
    Check if a file is an image based on its extension.
    """
    ext = os.path.splitext(filepath)[1].lower()
    return ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

def open_image(filepath):
    """
    Open an image file with Pillow and return the Image object.
    """
    if is_image_file(filepath) and os.path.exists(filepath):
        return Image.open(filepath)
    return None

def save_image(image: Image.Image, save_path: str, format="PNG"):
    """
    Save a PIL Image to the given path.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    image.save(save_path, format=format)

def resize_image(image: Image.Image, max_size=(300,300)):
    """
    Resize a PIL Image to fit within max_size, maintaining aspect ratio.
    """
    image.thumbnail(max_size)
    return image

def get_image_info(filepath):
    """
    Return basic info (width, height, format) about an image file.
    """
    if not is_image_file(filepath) or not os.path.exists(filepath):
        return None
    with Image.open(filepath) as img:
        return {
            "format": img.format,
            "size": img.size,  # (width, height)
            "mode": img.mode
        }


