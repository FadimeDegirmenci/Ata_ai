"""
ChromaDB entegrasyonu: Atatürk metinlerini parçalara bölüp vektör veritabanına kaydeder ve sorgular.
"""

import os
import re
import chromadb
from chromadb.utils import embedding_functions

# Yollar
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "ataturk_data.txt")
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# Sabitler
COLLECTION_NAME = "ataturk_koleksiyonu"
CHUNK_SIZE = 500
TEST_QUERY = "Atatürk nerede doğdu?"
TOP_K = 3


def metni_oku() -> str:
    """data/ataturk_data.txt dosyasını okur."""
    if not os.path.isfile(DATA_FILE):
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return f.read()


def parcalara_bol(metin: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Metni anlamlı parçalara böler. Mümkün olduğunca cümle sonlarında (.). böler.
    """
    metin = metin.strip()
    if not metin:
        return []

    parcalar = []
    # Önce çift satır sonlarına göre bloklara ayır (paragraflar)
    bloklar = re.split(r"\n\s*\n", metin)

    for blok in bloklar:
        blok = blok.strip()
        if not blok:
            continue
        if len(blok) <= chunk_size:
            parcalar.append(blok)
            continue
        # Uzun blokları cümle sınırlarında böl
        cumleler = re.split(r"(?<=[.!?])\s+", blok)
        mevcut = ""
        for cumle in cumleler:
            if len(mevcut) + len(cumle) + 1 <= chunk_size:
                mevcut = (mevcut + " " + cumle).strip() if mevcut else cumle
            else:
                if mevcut:
                    parcalar.append(mevcut)
                # Çok uzun tek cümle varsa karaktere göre böl
                if len(cumle) > chunk_size:
                    for i in range(0, len(cumle), chunk_size):
                        parcalar.append(cumle[i : i + chunk_size].strip())
                    mevcut = ""
                else:
                    mevcut = cumle
        if mevcut:
            parcalar.append(mevcut)

    return [p for p in parcalar if p.strip()]


def main():
    print("Veri dosyası okunuyor...")
    metin = metni_oku()
    parcalar = parcalara_bol(metin)
    print(f"  {len(parcalar)} parça oluşturuldu.")

    # ChromaDB istemcisi (kalıcı dizin)
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # Çok dilli embedding (Türkçe için)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        device="cpu",
    )

    # Koleksiyon: varsa silip yeniden oluştur (test için temiz başlangıç)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"description": "Atatürk hakkında metin parçaları"},
    )

    # Parçaları ekle (id'ler: chunk_0, chunk_1, ...)
    ids = [f"chunk_{i}" for i in range(len(parcalar))]
    collection.add(ids=ids, documents=parcalar)
    print(f"  '{COLLECTION_NAME}' koleksiyonuna {len(parcalar)} belge eklendi.")

    # Test sorusu
    print(f"\nTest sorusu: \"{TEST_QUERY}\"")
    print("En ilgili 3 sonuç:\n")
    sonuclar = collection.query(
        query_texts=[TEST_QUERY],
        n_results=TOP_K,
        include=["documents", "distances"],
    )

    for i, (doc, dist) in enumerate(
        zip(sonuclar["documents"][0], sonuclar["distances"][0]), start=1
    ):
        print(f"--- Sonuç {i} (mesafe: {dist:.4f}) ---")
        print(doc[:400] + ("..." if len(doc) > 400 else ""))
        print()

    print("ChromaDB işlemi tamamlandı.")


if __name__ == "__main__":
    main()
