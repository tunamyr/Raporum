# Raporum 🏥

Kan tahlili ve sağlık raporlarını PDF olarak yükleyin, sade Türkçe açıklama alın.

> ⚠️ Bu uygulama tıbbi tavsiye vermez. Sonuçlarınızı mutlaka doktorunuzla değerlendirin.

---

## Ne Yapar?

- PDF formatındaki kan tahlili veya sağlık raporunuzu yüklersiniz
- Yapay zeka her değeri analiz eder
- Her değer için şunları gösterir:
  - Normal mi, dikkat gerektiriyor mu, yüksek mi, düşük mü?
  - Sade Türkçe açıklama
  - Doktorunuza sormanız gereken soru

---

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini_2.5_Flash_Lite-4285F4?style=flat&logo=google&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)

## Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python, FastAPI |
| PDF Okuma | PyMuPDF |
| Yapay Zeka | Google Gemini 2.5 Flash Lite |
| Frontend | HTML, Tailwind CSS |

---

## Mimari

```mermaid
flowchart TD
    A([Kullanıcı]) -->|PDF + yaş + cinsiyet| B[Frontend\nHTML / JavaScript]
    B -->|POST /analyze\nmultipart/form-data| C[Backend\nFastAPI]
    C --> D{Rate Limiter\nslowapi\n10 istek/gün/IP}
    D -->|Limit aşıldı| E[429 Too Many Requests]
    D -->|OK| F[Doğrulama\nPDF mi? Boyut? Cinsiyet?]
    F -->|Geçersiz| G[400 Bad Request]
    F -->|Geçerli| H[parser.py\nPyMuPDF]
    H -->|Ham metin| I[analyzer.py]
    I -->|Metin XML etikete sarılır\nPrompt injection koruması| J[Google Gemini API\ngemini-2.5-flash-lite]
    J -->|JSON yanıt| K{Sağlık belgesi mi?}
    K -->|Hayır| L[422 Sağlık dışı belge]
    K -->|Evet| M[Sonuç JSON]
    M -->|Analiz sonucu| B
    B -->|Değer kartları\nözet + istatistik| A
    N[.env\nGEMINI_API_KEY] -.->|load_dotenv| I
```

## Kurulum (Lokal)

### 1. Repoyu klonla
```bash
git clone https://github.com/kullaniciadin/raporum.git
cd raporum
```

### 2. Bağımlılıkları kur
```bash
cd backend
pip install -r requirements.txt
```

### 3. API anahtarını ayarla
`backend/` klasörüne `.env` dosyası oluştur:
```
GEMINI_API_KEY=buraya_api_keyini_yaz
```
Gemini API anahtarını [Google AI Studio](https://aistudio.google.com)'dan ücretsiz alabilirsin.

### 4. Çalıştır
```bash
uvicorn main:app --reload --port 8000
```

Tarayıcıda `http://localhost:8000` adresine git.

---

## Kullanım

1. Ana sayfada PDF yükleme alanına raporunu sürükle-bırak ya da "Dosya Seç" butonuna tıkla
2. Analiz birkaç saniye sürer
3. Her değer için renk kodlu kart görünür:
   - 🟢 Yeşil → Normal
   - 🟡 Sarı → Dikkat
   - 🔴 Kırmızı → Yüksek veya Düşük
4. "Yeni Rapor Yükle" butonu ile tekrar başlayabilirsin

---

## Geliştirici

**Tuna Mayir**
