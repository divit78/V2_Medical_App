import os
from PIL import Image
from typing import Optional, Dict, Any, Tuple


class ImageValidator:
    """Handle image validation"""
    
    @staticmethod
    def is_image_file(filepath: str) -> bool:
        """Check if a file is an image based on its extension"""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Check if file exists"""
        return os.path.exists(filepath)


class ImageProcessor:
    """Handle image processing operations"""
    
    def __init__(self):
        self.validator = ImageValidator()
    
    def open_image(self, filepath: str) -> Optional[Image.Image]:
        """Open an image file with Pillow"""
        if (self.validator.is_image_file(filepath) and 
            self.validator.file_exists(filepath)):
            return Image.open(filepath)
        return None
    
    def save_image(self, image: Image.Image, save_path: str, format: str = "PNG") -> None:
        """Save a PIL Image to the given path"""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        image.save(save_path, format=format)
    
    def resize_image(self, image: Image.Image, max_size: Tuple[int, int] = (300, 300)) -> Image.Image:
        """Resize a PIL Image maintaining aspect ratio"""
        image.thumbnail(max_size)
        return image
    
    def get_image_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Return basic info about an image file"""
        if (not self.validator.is_image_file(filepath) or 
            not self.validator.file_exists(filepath)):
            return None
        
        with Image.open(filepath) as img:
            return {
                "format": img.format,
                "size": img.size,  # (width, height)
                "mode": img.mode
            }


# Global image processor instance
image_processor = ImageProcessor()


# Keep original functions for backward compatibility
def is_image_file(filepath: str) -> bool:
    """Check if a file is an image based on its extension"""
    return ImageValidator.is_image_file(filepath)


def open_image(filepath: str) -> Optional[Image.Image]:
    """Open an image file with Pillow and return the Image object"""
    return image_processor.open_image(filepath)


def save_image(image: Image.Image, save_path: str, format: str = "PNG") -> None:
    """Save a PIL Image to the given path"""
    image_processor.save_image(image, save_path, format)


def resize_image(image: Image.Image, max_size: Tuple[int, int] = (300, 300)) -> Image.Image:
    """Resize a PIL Image to fit within max_size, maintaining aspect ratio"""
    return image_processor.resize_image(image, max_size)


def get_image_info(filepath: str) -> Optional[Dict[str, Any]]:
    """Return basic info (width, height, format) about an image file"""
    return image_processor.get_image_info(filepath)
