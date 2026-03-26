# Raporum
Sağlık raporlarınızı PDF olarak yükleyip Türkçe
açıklama alabileceğiniz web uygulaması.

## Kurulum
1. pip install -r backend/requirements.txt
2. backend/ klasörüne .env dosyası oluştur: GEMINI_API_KEY=...
3. uvicorn backend.main:app --reload
4. frontend/index.html dosyasını aç

.env dosyası .gitignore'a eklenmiştir, repoya gitmez.
