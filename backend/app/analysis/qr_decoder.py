import io
from PIL import Image, ImageOps
from pyzbar.pyzbar import decode as pyzbar_decode
from typing import Dict, Any, Optional, Tuple

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB max
ALLOWED_IMAGE_FORMATS = {"PNG", "JPEG", "JPG", "WEBP", "BMP", "GIF"}

class QRDecodeResult:
    def __init__(
        self,
        success: bool,
        error_message: Optional[str] = None,
        decoded_text: Optional[str] = None,
        payload_type: str = "UNKNOWN", # 'URL' or 'TEXT'
        image_format: str = "",
        image_size_bytes: int = 0
    ):
        self.success = success
        self.error_message = error_message
        self.decoded_text = decoded_text
        self.payload_type = payload_type
        self.image_format = image_format
        self.image_size_bytes = image_size_bytes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "error_message": self.error_message,
            "decoded_text": self.decoded_text,
            "payload_type": self.payload_type,
            "image_format": self.image_format,
            "image_size_bytes": self.image_size_bytes
        }


def decode_qr_image_bytes(image_bytes: bytes) -> QRDecodeResult:
    """
    Validates and decodes a QR code image buffer.
    Enforces 5MB size limit and PIL image format verification.
    """
    if not image_bytes:
        return QRDecodeResult(success=False, error_message="Empty image file provided.")

    file_size = len(image_bytes)
    if file_size > MAX_FILE_SIZE_BYTES:
        return QRDecodeResult(
            success=False,
            error_message=f"Image file size ({file_size} bytes) exceeds 5MB limit.",
            image_size_bytes=file_size
        )

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img_format = (img.format or "").upper()

        if img_format not in ALLOWED_IMAGE_FORMATS and img_format != "MPO":
            return QRDecodeResult(
                success=False,
                error_message=f"Unsupported image format '{img_format}'. Allowed formats: PNG, JPEG, WEBP, BMP, GIF.",
                image_format=img_format,
                image_size_bytes=file_size
            )

        # Convert image to RGB/L for barcode processing
        img_converted = img.convert("L")

        # Decode using pyzbar
        decoded_objects = pyzbar_decode(img_converted)

        # Try inverted image if initial decode returns nothing
        if not decoded_objects:
            img_inverted = ImageOps.invert(img_converted)
            decoded_objects = pyzbar_decode(img_inverted)

        if not decoded_objects:
            return QRDecodeResult(
                success=False,
                error_message="No valid QR code detected in the uploaded image.",
                image_format=img_format,
                image_size_bytes=file_size
            )

        decoded_data = decoded_objects[0].data.decode("utf-8", errors="replace").strip()

        # Classify payload type (URL or TEXT)
        payload_type = "URL" if (decoded_data.startswith("http://") or decoded_data.startswith("https://") or decoded_data.startswith("www.")) else "TEXT"

        return QRDecodeResult(
            success=True,
            decoded_text=decoded_data,
            payload_type=payload_type,
            image_format=img_format,
            image_size_bytes=file_size
        )

    except Exception as exc:
        return QRDecodeResult(
            success=False,
            error_message=f"Invalid or corrupted image file: {str(exc)}",
            image_size_bytes=file_size
        )
