from dotenv import load_dotenv

# .env dosyasını uygulama başlarken yükle
load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from analyzer import analyze_report
from parser import extract_text, pdf_to_images

# Günlük maksimum dosya boyutu: 10 MB
MAX_DOSYA_BOYUTU = 10 * 1024 * 1024

# IP başına günlük istek limiti — .env'den okunur, varsayılan 10
import os
GUNLUK_LIMIT = os.getenv("GUNLUK_LIMIT", "10")

# Rate limiter: istemcinin IP adresini anahtar olarak kullan
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Raporum API")


async def rate_limit_handler(_request: Request, _exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Günlük istek limitinize ulaştınız. Lütfen yarın tekrar deneyin."},
    )


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

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
    yas: int = Form(None),
    cinsiyet: str = Form(None),
    sikayet: str = Form(None),
):
    """
    PDF dosyasını, yaş ve cinsiyeti alır; metin çıkarır ve Gemini ile analiz eder.
    Her IP adresi günde en fazla GUNLUK_LIMIT kadar istek atabilir.
    """

    DESTEKLENEN_FORMATLAR = {
        ".pdf":  "pdf",
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
    }

    # Cinsiyet değeri kontrolü (gönderilmişse geçerli olmalı)
    if cinsiyet is not None and cinsiyet not in ("erkek", "kadin"):
        raise HTTPException(
            status_code=400,
            detail="Cinsiyet 'erkek' veya 'kadin' olmalıdır.",
        )

    # Format kontrolü
    uzanti = os.path.splitext(file.filename.lower())[1]
    if uzanti not in DESTEKLENEN_FORMATLAR:
        raise HTTPException(
            status_code=400,
            detail="Yalnızca PDF, JPEG ve PNG dosyaları kabul edilmektedir.",
        )

    # Dosya içeriğini oku
    dosya_icerigi = await file.read()

    # Dosya boyutu kontrolü (frontend'i atlayıp direkt API'ye gelen istekler için)
    if len(dosya_icerigi) > MAX_DOSYA_BOYUTU:
        raise HTTPException(
            status_code=400,
            detail="Dosya boyutu 10 MB'ı aşamaz.",
        )

    # PDF → metin çıkar; görsel → doğrudan Gemini'ye gönder
    dosya_turu = DESTEKLENEN_FORMATLAR[uzanti]
    try:
        if dosya_turu == "pdf":
            ham_metin = extract_text(dosya_icerigi, file.filename)
            if ham_metin:
                sonuc = analyze_report(raw_text=ham_metin, yas=yas, cinsiyet=cinsiyet, sikayet=sikayet)
            else:
                # Taranmış PDF — sayfaları görsel olarak işle
                gorsel_listesi = pdf_to_images(dosya_icerigi)
                sonuc = analyze_report(image_list=gorsel_listesi, yas=yas, cinsiyet=cinsiyet, sikayet=sikayet)
        else:
            sonuc = analyze_report(image_bytes=dosya_icerigi, image_mime=dosya_turu, yas=yas, cinsiyet=cinsiyet, sikayet=sikayet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz sırasında bir hata oluştu: {str(e)}")

    # Sağlık dışı belge kontrolü
    if sonuc.get("saglik_disi"):
        raise HTTPException(
            status_code=422,
            detail="Bu belge bir sağlık raporu değil. Lütfen kan tahlili, EKG, ultrason gibi tıbbi bir belge yükleyin.",
        )

    return sonuc
