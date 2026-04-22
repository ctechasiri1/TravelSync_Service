import uuid
from enum import Enum
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image, ImageOps

# ==========================================
# ENUMS & CONFIGURATION
# ==========================================

# Strictly limit what type of files can be saved to your server
ALLOW_DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".csv"}


class DocumentType(Enum):
    TRIP_DOC = Path("media/documents")

    def __init__(self, dir_path: Path):
        self.dir_path = dir_path


class ImageType(Enum):
    """
    Defines the strict dimensions and storage directories for different iamge assets.
    Acts as a configuration blueprint to ensure uniformity across the platform.
    """

    # MEMBER = (Directory Path, Width, Height)
    PROFILE = (Path("media/profile_images"), 300, 300)
    COVER = (Path("media/cover_images"), 1200, 600)
    RECEIPT = (Path("media/receipt"), 500, 500)

    def __init__(self, dir_path: Path, width: int, height: int):
        self.dir_path = dir_path
        self.width = width
        self.height = height

    @property
    def size(self) -> tuple[int, int]:
        """Convenience property that formats dimensions for the Pillow library."""
        return (self.width, self.height)


# ==========================================
# THE SERVICE LAYER
# ==========================================


class LocalMediaService:
    """Handles processing, saving, and deleting ALL media on the local server disk."""

    # --- PUBLIC ASYNC METHODS (Called by your Trip/Expense Services) ---

    async def proces_image(self, file: UploadFile, image_type: ImageType) -> str:
        """Processes and saves an image asynchronously."""
        raw_bytes = await file.read()
        return await run_in_threadpool(self._sync_process_image, raw_bytes, image_type)

    async def process_document(
        self, file: UploadFile, document_type: DocumentType
    ) -> str:
        raw_bytes = await file.read()
        original_filename = file.filename or ""

        return await run_in_threadpool(
            self._sync_process_document, original_filename, raw_bytes, document_type
        )

    async def delete_file(
        self, filename: str | None, media_type: ImageType | DocumentType
    ) -> None:
        if not filename:
            return

        await run_in_threadpool(self._sync_delete_file, filename, media_type)

    # --- PRIVATE SYNCHRONOUS METHODS (The heavy lifting) ---

    def _sync_process_image(self, content: bytes, image_type: ImageType) -> str:
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

    def _sync_process_document(
        self, content: bytes, original_filename: str, doc_type: DocumentType
    ) -> str:
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

    def _sync_delete_file(
        self, filename: str, image_type: ImageType | DocumentType
    ) -> None:
        """
        Safely removes an image file form the server's hard drive.
        Fails silently if the file does not exist or not filename is provided
        """
        filepath = image_type.dir_path / filename
        if filepath.exists():
            filepath.unlink()
