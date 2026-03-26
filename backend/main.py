from dotenv import load_dotenv

# .env dosyasını uygulama başlarken yükle
load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_report
from parser import extract_text

app = FastAPI(title="Raporum API")

# Tüm originlere CORS izni ver (geliştirme ortamı için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Sağlık kontrolü endpoint'i."""
    return {"durum": "Raporum API çalışıyor"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    PDF dosyasını alır, metin çıkarır ve Gemini ile analiz eder.
    Multipart/form-data formatında 'file' alanı beklenir.
    """

    # Sadece PDF kabul et
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Yalnızca PDF dosyaları kabul edilmektedir.",
        )

    # Dosya içeriğini oku
    dosya_icerigi = await file.read()

    # PDF'den metin çıkar
    try:
        ham_metin = extract_text(dosya_icerigi, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Metni analiz et
    try:
        sonuc = analyze_report(ham_metin)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analiz sırasında bir hata oluştu: {str(e)}",
        )

    return sonuc
