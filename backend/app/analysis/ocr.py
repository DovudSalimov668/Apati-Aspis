import io
from PIL import Image
from typing import Dict, Any, Optional

class OCRResult:
    def __init__(
        self,
        available: bool,
        extracted_text: Optional[str] = None,
        error_message: Optional[str] = None,
        status: str = "COMPLETED" # 'COMPLETED', 'OCR_UNAVAILABLE', 'FAILED'
    ):
        self.available = available
        self.extracted_text = extracted_text
        self.error_message = error_message
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "extracted_text": self.extracted_text,
            "error_message": self.error_message,
            "status": self.status
        }


def extract_text_from_image_bytes(image_bytes: bytes) -> OCRResult:
    """
    Attempts local OCR text extraction from image buffer using pytesseract if installed/configured.
    Gracefully degrades to isolated OCR_UNAVAILABLE status if local binary is uninstalled.
    """
    if not image_bytes:
        return OCRResult(available=False, error_message="Empty image provided.", status="FAILED")

    try:
        import pytesseract
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img).strip()
        return OCRResult(
            available=True,
            extracted_text=text,
            status="COMPLETED"
        )
    except ImportError:
        return OCRResult(
            available=False,
            error_message="Local pytesseract OCR module is not installed.",
            status="OCR_UNAVAILABLE"
        )
    except Exception as exc:
        return OCRResult(
            available=False,
            error_message=f"OCR processing failed or binary missing: {str(exc)}",
            status="OCR_UNAVAILABLE"
        )
