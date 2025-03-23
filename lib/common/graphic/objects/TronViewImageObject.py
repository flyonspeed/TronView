import os
from dataclasses import dataclass
from typing import Optional
import io
import base64
from PIL import Image

@dataclass
class TronViewImageObject:
    """Class for storing image information"""
    file_name: str
    file_path: str
    file_type: str = "image"
    file_size: Optional[int] = None
    base64: Optional[str] = None

    width: Optional[int] = None
    height: Optional[int] = None

    def __post_init__(self):
        """Calculate file size if not provided"""
        if self.file_size is None and os.path.exists(self.file_path):
            self.file_size = os.path.getsize(self.file_path)

    def to_dict(self) -> dict:
        """Convert the object to a dictionary representation"""
        return {
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "base64": self.base64
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TronViewImageObject':
        """Create an instance from a dictionary"""
        # if no width and height.. figure it out based on the base64
        if 'width' not in data or 'height' not in data:
            # use PIL to get the width and height.  load from base64
            if data['base64']:
                image = Image.open(io.BytesIO(base64.b64decode(data['base64'])))
            else:
                # else error
                raise ValueError("No base64 data provided")
            data['width'] = image.width
            data['height'] = image.height
            print(f"calculated width: {data['width']}, height: {data['height']}")
        return cls(**data)
