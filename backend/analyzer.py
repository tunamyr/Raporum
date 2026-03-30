import json
import os
import re

import google.generativeai as genai
from dotenv import load_dotenv

# .env dosyasını yükle (Replit Secrets ile de uyumlu çalışır)
load_dotenv()

# System prompt: modele rolünü ve çıktı formatını tanımlar
SYSTEM_PROMPT = """
Sen bir sağlık raporu açıklama asistanısın. Kullanıcıdan gelen
ham rapor metnini analiz edip her tespit edilen değer için
JSON formatında yanıt ver.

Yanıtını sanki hastaya doğrudan konuşur gibi yaz. Tıbbi terim kullanma,
günlük hayatta herkesin anlayacağı sade Türkçe kullan. "Eritrosit" yerine
"kırmızı kan hücresi", "hemoglobin" için "kanda oksijen taşıyan madde" gibi.

Yanıt formatı (başka hiçbir şey yazma, sadece JSON):
{
  "ozet": "Raporun genel tablosunu anlatan 4-6 cümlelik değerlendirme. Hangi değerler dikkat çekiyor, genel sağlık tablosu ne durumda, hasta için en önemli 1-2 bulgу nedir — bunları sade Türkçe, sanki bir arkadaşına anlatır gibi yaz. Tıbbi terim kullanma.",
  "degerler": [
    {
      "ad": "değer adı (anlaşılır Türkçe karşılığıyla)",
      "sonuc": "ölçülen değer + birim",
      "referans": "normal aralık",
      "durum": "normal | dikkat | yuksek | dusuk",
      "aciklama": "Bu değer ne işe yarar, sade Türkçe 1-2 cümle",
      "neden": "SADECE durum 'yuksek', 'dusuk' veya 'dikkat' ise doldur: Bu değer neden bu seviyede olabilir? Olası 2-3 nedeni sade Türkçe yaz. Durum 'normal' ise bu alanı kesinlikle boş string olarak bırak: \"\"",
      "belirtiler": "SADECE durum 'yuksek', 'dusuk' veya 'dikkat' ise doldur: Bu değerin bu seviyede olması vücutta ne gibi belirtilere yol açabilir? Sade Türkçe yaz. Durum 'normal' ise bu alanı kesinlikle boş string olarak bırak: \"\"",
      "tekrar_test": "Bu değer için ne kadar sürede tekrar test yapılması önerilir? (örn: '2 haftada bir', '3 ayda bir', 'yılda bir' gibi). Değer normalse 'Rutin kontrol yeterli' yaz.",
      "doktor_sorusu": "bu değer için doktora sorulabilecek en iyi soru"
    }
  ],
  "uyari": "Bu analiz tıbbi tavsiye değildir. Sonuçlarınızı mutlaka doktorunuzla değerlendirin."
}
"""


def analyze_report(raw_text: str, yas: int = None, cinsiyet: str = None) -> dict:
    """Ham rapor metnini Gemini API ile analiz eder ve JSON döndürür."""

    # Ortam değişkeninden API anahtarını oku
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY ortam değişkeni tanımlı değil.")

    # Gemini istemcisini yapılandır
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=SYSTEM_PROMPT,
    )

    # Yaş ve cinsiyet bilgisini rapora ekle
    cinsiyet_tr = "Erkek" if cinsiyet == "erkek" else "Kadın"
    hasta_bilgisi = f"Hasta bilgisi: {yas} yaşında {cinsiyet_tr}.\n\n"
    icerik = hasta_bilgisi + raw_text

    # Modele rapor metnini gönder
    response = model.generate_content(icerik)
    yanit_metni = response.text.strip()

    # ```json ... ``` bloklarını temizle
    temiz_metin = re.sub(r"```json\s*", "", yanit_metni)
    temiz_metin = re.sub(r"```\s*", "", temiz_metin).strip()

    # JSON parse et; hata olursa ham metni döndür
    try:
        return json.loads(temiz_metin)
    except json.JSONDecodeError:
        return {"raw_response": yanit_metni}
