import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

from enum import Enum

class ImageType(Enum):
    # MEMBER = (Directory Path, Width, Height)
    PROFILE = (Path("media/profile_pics"), 300, 300)
    COVER = (Path("media/cover_pics"), 1200, 600)

    def __init__(self, dir_path: Path, width: int, height: int):
        self.dir_path = dir_path
        self.width = width
        self.height = height
    
    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

def process_image(content: bytes, image_type: ImageType) -> str:
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(img, image_type.size, method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = image_type.dir_path / filename

        image_type.dir_path.mkdir(parents=True, exist_ok=True)

        img.save(filepath, "JPEG", quality=85, optimize=True)
    
    return filename

def delete_image(filename: str | None, image_type: ImageType) -> None:
    if filename is None:
        return
    
    filepath = image_type.dir_path / filename
    if filepath.exists():
        filepath.unlink()
