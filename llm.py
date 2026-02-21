"""
Groq LLM entegrasyonu: Kullanıcı sorusu → ChromaDB'den ilgili parçalar → Groq ile Atatürk üslubunda yanıt.
"""

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

import chromadb
from groq import Groq

from vector_db import CHROMA_PERSIST_DIR, COLLECTION_NAME

GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 3

SISTEM_PROMPTU = """Sen Mustafa Kemal Atatürk'sün. 1881'de Selanik'te doğdun. Türkiye Cumhuriyeti'nin kurucususun. Sana verilen kaynak bilgilere dayanarak soruları Atatürk'ün ağırbaşlı ve kararlı üslubuyla, Türkçe olarak cevapla. Kaynaklarda olmayan konularda 'Bu konuda size kesin bilgi veremem' de."""


def _get_collection():
    """ChromaDB kalıcı istemcisi ve ataturk_koleksiyonu döndürür."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_collection(name=COLLECTION_NAME)


def _kaynak_parcalari_cek(soru: str) -> list[str]:
    """Soruya göre ChromaDB'den en ilgili TOP_K parçayı döndürür."""
    collection = _get_collection()
    sonuc = collection.query(
        query_texts=[soru],
        n_results=TOP_K,
        include=["documents"],
    )
    docs = sonuc.get("documents")
    if not docs or not docs[0]:
        return []
    return docs[0]


def soru_cevapla(soru: str) -> str:
    """
    Kullanıcı sorusunu alır; ChromaDB'den ilgili 3 parçayı çeker,
    Groq (llama3-70b-8192) ile sistem promptuna göre cevap üretir ve döndürür.
    """
    soru = (soru or "").strip()
    if not soru:
        return "Lütfen bir soru yazın."

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Hata: GROQ_API_KEY .env dosyasında tanımlı değil."

    parcalar = _kaynak_parcalari_cek(soru)
    kaynak_metni = "\n\n".join(f"[{i+1}] {p}" for i, p in enumerate(parcalar, 1))
    if not kaynak_metni:
        kaynak_metni = "(Kaynak parçası bulunamadı.)"

    user_icerik = f"""Aşağıdaki kaynak parçalarına göre soruyu yanıtla.

Kaynaklar:
{kaynak_metni}

Soru: {soru}"""

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SISTEM_PROMPTU},
                {"role": "user", "content": user_icerik},
            ],
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception as e:
        return f"Hata (Groq/LLM): {e}"


# Test / arayüz için aynı fonksiyonun alternatif adı
ataturk_cevapla = soru_cevapla


if __name__ == "__main__":
    test_sorusu = "Atatürk, bize kendinizi tanıtır mısınız?"
    print(f"Soru: {test_sorusu}")
    print("-" * 50)
    cevap = ataturk_cevapla(test_sorusu)
    print(f"Atatürk: {cevap}")
