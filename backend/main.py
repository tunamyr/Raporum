from dotenv import load_dotenv

# .env dosyasını uygulama başlarken yükle
load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from analyzer import analyze_report
from parser import extract_text

# Günlük maksimum dosya boyutu: 10 MB
MAX_DOSYA_BOYUTU = 10 * 1024 * 1024

# IP başına günlük istek limiti — .env'den okunur, varsayılan 10
import os
GUNLUK_LIMIT = os.getenv("GUNLUK_LIMIT", "10")

# Rate limiter: istemcinin IP adresini anahtar olarak kullan
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Raporum API")

# Rate limit aşıldığında 429 döndür
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Tüm originlere CORS izni ver
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
@limiter.limit(f"{GUNLUK_LIMIT}/day")
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    yas: int = Form(...),
    cinsiyet: str = Form(...),
):
    """
    PDF dosyasını, yaş ve cinsiyeti alır; metin çıkarır ve Gemini ile analiz eder.
    Her IP adresi günde en fazla GUNLUK_LIMIT kadar istek atabilir.
    """

    # Cinsiyet değeri kontrolü
    if cinsiyet not in ("erkek", "kadin"):
        raise HTTPException(
            status_code=400,
            detail="Cinsiyet 'erkek' veya 'kadin' olmalıdır.",
        )
 
    # Sadece PDF kabul et
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Yalnızca PDF dosyaları kabul edilmektedir.",
        )

    # Dosya içeriğini oku
    dosya_icerigi = await file.read()

    # Dosya boyutu kontrolü (frontend'i atlayıp direkt API'ye gelen istekler için)
    if len(dosya_icerigi) > MAX_DOSYA_BOYUTU:
        raise HTTPException(
            status_code=400,
            detail="Dosya boyutu 10 MB'ı aşamaz.",
        )

    # PDF'den metin çıkar
    try:
        ham_metin = extract_text(dosya_icerigi, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Metni analiz et (yaş ve cinsiyet bilgisiyle)
    try:
        sonuc = analyze_report(ham_metin, yas=yas, cinsiyet=cinsiyet)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analiz sırasında bir hata oluştu: {str(e)}",
        )

    return sonuc
