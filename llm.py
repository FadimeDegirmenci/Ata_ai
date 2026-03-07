"""
llm.py - Ollama ile Atatürk Chatbot (API gerektirmez)
"""

import ollama
import chromadb
from chromadb.utils import embedding_functions
import os

# ChromaDB ve embedding modelini bir kez yükle
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
MODEL_NAME = "qwen2.5:3b"


ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    name="ataturk_koleksiyonu",
    embedding_function=ef
)
SYSTEM_PROMPT = """Sen Mustafa Kemal Atatürk'sün. Birinci şahıs olarak konuş, yani "Ben..." diye başla.
Asla üçüncü şahıs kullanma. Asla kaynak, link, tarih veya referans belirtme.
Asla "Atatürk şöyle dedi" gibi ifadeler kullanma.
Sana verilen kaynak bilgilere dayanarak kendi sözlerinle, doğal bir şekilde cevap ver.
Türkçe, kısa, akıcı ve ağırbaşlı bir üslupla konuş.
Kaynaklarda olmayan konularda sadece 'Bu konuda size kesin bilgi veremem.' de."""

def ataturk_cevapla(soru: str) -> str:
    try:
        results = collection.query(query_texts=[soru], n_results=3)
        parcalar = results["documents"][0] if results["documents"] else []
        baglam = "\n\n".join(parcalar)

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + f"\n\nKaynak bilgiler:\n{baglam}"},
                {"role": "user", "content": soru}
            ],
            options={"temperature": 0.7}
        )
        cevap = response["message"]["content"]
        if not cevap or not cevap.strip():
            return "Yanıt alınamadı, tekrar deneyin."
        return cevap

    except Exception as e:
        return f"Hata: {e}"


if __name__ == "__main__":
    test = "Atatürk, bize kendinizi tanıtır mısınız?"
    print(f"Soru: {test}")
    print("-" * 50)
    print(f"Atatürk: {ataturk_cevapla(test)}")