# Raporum 🏥

Kan tahlili ve sağlık raporlarını yükleyin; konsültan hekim denetimli yapay zeka analizi ile sade Türkçe açıklama alın.

> ⚠️ Bu uygulama tıbbi tavsiye vermez. Sonuçlarınızı mutlaka doktorunuzla değerlendirin.

---

## Ne Yapar?

- PDF, JPEG veya PNG formatındaki sağlık raporunuzu yüklersiniz
- Konsültan hekim kadrosu ve tıbbi yapay zeka her değeri birlikte inceler
- Her değer için şunlar gösterilir:
  - Normal mi, dikkat gerektiriyor mu, yüksek mi, düşük mü?
  - Referans aralığı görseli (bar/gauge)
  - Sade Türkçe açıklama
  - Olası nedenler ve belirtiler
  - Doktorunuza sormanız gereken soru
- Yaş, cinsiyet ve şikayetlerinize göre kişiselleştirilmiş analiz
- Dikkatli/anormal değerlere göre filtreleme

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
| Görsel İşleme | Pillow |
| Yapay Zeka | Google Gemini 2.5 Flash Lite |
| Frontend | HTML, Tailwind CSS |

---

## Mimari

```mermaid
flowchart TD
    A([Kullanıcı]) -->|Dosya + yaş? + cinsiyet? + şikayet?| B[Frontend\nHTML / JavaScript]

    B -->|POST /analyze\nmultipart/form-data| C[Backend\nFastAPI]

    C --> D{Rate Limiter\nslowapi\n10 istek/gün/IP}
    D -->|Limit aşıldı| E[429 Too Many Requests]
    D -->|OK| F[Doğrulama\nFormat? Boyut? Cinsiyet geçerli mi?]

    F -->|Geçersiz| G[400 Bad Request]
    F -->|PDF| H[parser.py\nPyMuPDF]
    F -->|JPEG / PNG| I2[analyzer.py\nGörsel olarak gönder]

    H -->|Metin çıkarıldı| I[analyzer.py]
    H -->|Taranmış PDF — metin yok| H2[pdf_to_images\nSayfalar görsele dönüştürülür]
    H2 -->|Görsel listesi| I

    I --> J{Yaş / cinsiyet / şikayet\ngirildi mi?}
    J -->|Evet| K[Kişiselleştirilmiş\nhasta bilgisi satırı]
    J -->|Hayır| L[Genel analiz]
    K --> M
    L --> M

    M[Metin XML etiketle sarılır\nPrompt injection koruması]
    M -->|İstek| N[Google Gemini API\ngemini-2.5-flash-lite]

    N -->|JSON yanıt| O{Sağlık belgesi mi?}
    O -->|Hayır| P[422 Sağlık dışı belge]
    O -->|Evet| Q[Sonuç JSON]

    Q -->|Analiz sonucu| B
    B -->|Değer kartları\nreferans barı + filtre + özet| A

    R[.env\nGEMINI_API_KEY] -.->|load_dotenv| I
    I2 --> M
```

## Kurulum (Lokal)

### 1. Repoyu klonla
```bash
git clone https://github.com/tunamyr/Raporum.git
cd Raporum
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

1. Yaş, cinsiyet ve şikayetlerini gir (isteğe bağlı)
2. PDF, JPEG veya PNG formatındaki raporunu sürükle-bırak ya da tıklayarak seç
3. "Analizi Başlat" butonuna bas
4. Her değer için renk kodlu kart görünür:
   - 🟢 Yeşil → Normal
   - 🟡 Sarı → Dikkat
   - 🔴 Kırmızı → Yüksek veya Düşük
5. Anormal değerleri filtrelemek için "Yalnızca dikkat edenler" butonunu kullan
6. "Yeni Rapor Yükle" butonu ile tekrar başlayabilirsin

---

## Geliştirici

**Tuna Mayir**
