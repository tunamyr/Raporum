import io

import fitz  # PyMuPDF
from PIL import Image


def extract_text(file_bytes: bytes, filename: str) -> str:
    """PDF dosyasından metin çıkarır. Metin yoksa None döndürür."""

    if not filename.lower().endswith(".pdf"):
        raise ValueError("Yalnızca PDF dosyaları desteklenmektedir.")

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    sayfalarin_metni = []

    for sayfa_no in range(len(doc)):
        sayfa = doc[sayfa_no]
        metin = sayfa.get_text("text")
        if metin.strip():
            sayfalarin_metni.append(metin)

    doc.close()
    tam_metin = "\n".join(sayfalarin_metni).strip()
    return tam_metin if tam_metin else None


def pdf_to_images(file_bytes: bytes) -> list:
    """Taranmış PDF sayfalarını PIL Image listesine çevirir."""

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    mat = fitz.Matrix(2, 2)  # 2x zoom — daha iyi görüntü kalitesi
    images = []

    for sayfa_no in range(len(doc)):
        sayfa = doc[sayfa_no]
        pix = sayfa.get_pixmap(matrix=mat)
        images.append(Image.open(io.BytesIO(pix.tobytes("png"))))

    doc.close()
    return images
