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

Yanıt formatı (başka hiçbir şey yazma, sadece JSON):
{
  "ozet": "2-3 cümlelik genel değerlendirme",
  "degerler": [
    {
      "ad": "değer adı",
      "sonuc": "ölçülen değer + birim",
      "referans": "normal aralık",
      "durum": "normal | dikkat | yuksek | dusuk",
      "aciklama": "sade Türkçe, 1-2 cümle",
      "doktor_sorusu": "bu değer için doktora sorulabilecek en iyi soru"
    }
  ],
  "uyari": "Bu analiz tıbbi tavsiye değildir. Sonuçlarınızı mutlaka doktorunuzla değerlendirin."
}
"""


def analyze_report(raw_text: str) -> dict:
    """Ham rapor metnini Gemini API ile analiz eder ve JSON döndürür."""

    # Ortam değişkeninden API anahtarını oku
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY ortam değişkeni tanımlı değil.")

    # Gemini istemcisini yapılandır
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    # Modele rapor metnini gönder
    response = model.generate_content(raw_text)
    yanit_metni = response.text.strip()

    # ```json ... ``` bloklarını temizle
    temiz_metin = re.sub(r"```json\s*", "", yanit_metni)
    temiz_metin = re.sub(r"```\s*", "", temiz_metin).strip()

    # JSON parse et; hata olursa ham metni döndür
    try:
        return json.loads(temiz_metin)
    except json.JSONDecodeError:
        return {"raw_response": yanit_metni}
