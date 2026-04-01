import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

from enum import Enum

# ==========================================
# DOCUMENT PROCESSING
# ==========================================

class DocumentType(Enum):
    TRIP_DOC = Path("media/documents")

    def __init__(self, dir_path: Path):
        self.dir_path = dir_path

# Strictly limit what type of files can be saved to your server
ALLOW_DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".csv"}


def process_document(content: bytes, original_filename: str, doc_type: DocumentType) -> str:
    """
    Securely saves a raw document (like a PDF) to the server.
    Extracts the original extension, generates a safe UUID filename, and writes the bytes. 
    """
    # 1. Extract the extension (e.g., 'pdf') and make it lowercase
    ext = Path(original_filename).suffix.lower()

    # 2. Security Check: Block unsupported files
    if ext not in ALLOW_DOCUMENT_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    
    # 3. Generate a mathematically safe filename
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = doc_type.dir_path / filename

    # 4. Ensure the media/document directory actually exists
    doc_type.dir_path.mkdir(parents=True, exist_ok=True)

    # 5. Write the raw bytes directly to the hard drive
    with open(filepath, "wb") as f:
        f.write(content)

    return filename


def delete_document(filename: str | None, doc_type: DocumentType) -> None:
    """Remove a document from the hard drive."""
    if filename is None:
        return

    filepath = doc_type.dir_path / filename
    if filepath.exists():
        filepath.unlink()


# ==========================================
# IMAGE PROCESSING
# ==========================================

class ImageType(Enum):
    """
    Defines the strict dimensions and storage directories for different iamge assets.
    Acts as a configuration blueprint to ensure uniformity across the platform.
    """
    # MEMBER = (Directory Path, Width, Height)
    PROFILE = (Path("media/profile_images"), 300, 300)
    COVER = (Path("media/cover_images"), 1200, 600)

    def __init__(self, dir_path: Path, width: int, height: int):
        self.dir_path = dir_path
        self.width = width
        self.height = height
    
    @property
    def size(self) -> tuple[int, int]:
        """Convenience property that formats dimensions for the Pillow library."""
        return (self.width, self.height)


def process_image(content: bytes, image_type: ImageType) -> str:
    """
    Processes a raw image upload for secure storage and optimized delivery.
    Returns the generated UUID filename (e.g. 'a1b2c3d4.jpg') to saved in the database.
    """
    # 1. Read the raw bytes into a Pillow Image object
    with Image.open(BytesIO(content)) as original:

        # 2. Correct EXIF orientation (prevents mobile uploads from rotating sideways)
        img = ImageOps.exif_transpose(original)

        # 3. Crop and resize the image to the strict dimensions of the ImageType
        img = ImageOps.fit(img, image_type.size, method=Image.Resampling.LANCZOS)

        # 4. Strip transparency (RGBA to RGB) to allow for sage JPEG compression
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        # 5. Generate a mathematically safe UUID filename to prevent directory traversal
        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = image_type.dir_path / filename

        # 6. Ensure the target media directory actually exists
        image_type.dir_path.mkdir(parents=True, exist_ok=True)

        # 7. Save the optimized JPEG directly to the hard drive
        img.save(filepath, "JPEG", quality=85, optimize=True)
    
    return filename


def delete_image(filename: str | None, image_type: ImageType) -> None:
    """
    Safely removes an image file form the server's hard drive.
    Fails silently if the file does not exist or not filename is provided
    """
    if filename is None:
        return
    
    filepath = image_type.dir_path / filename
    if filepath.exists():
        filepath.unlink()
