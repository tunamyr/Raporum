import fitz  # PyMuPDF


def extract_text(file_bytes: bytes, filename: str) -> str:
    """PDF dosyasından metin çıkarır."""

    # Sadece PDF dosyaları kabul edilir
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Yalnızca PDF dosyaları desteklenmektedir.")

    # PyMuPDF ile PDF'i bellekten aç
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    sayfalarin_metni = []

    for sayfa_no in range(len(doc)):
        sayfa = doc[sayfa_no]
        # UTF-8 uyumlu metin çıkar
        metin = sayfa.get_text("text")
        if metin.strip():
            sayfalarin_metni.append(metin)

    doc.close()

    tam_metin = "\n".join(sayfalarin_metni).strip()

    # Metin boşsa hata fırlat
    if not tam_metin:
        raise ValueError(
            "PDF'den metin çıkarılamadı. Dosya taranmış görsel içeriyor olabilir."
        )

    return tam_metin
