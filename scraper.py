"""
Atatürk hakkında web scraping modülü.
Türkçe Wikipedia ve ataturk.net'ten metin çeker, temizler ve data/ataturk_data.txt'ye yazar.
"""

import os
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

# Kaynak URL'leri
WIKIPEDIA_URL = "https://tr.wikipedia.org/wiki/Mustafa_Kemal_Atatürk"
ATATURK_NET_URL = "https://www.ataturk.net"

# İstek başlıkları (engellemeyi azaltmak için)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

# Çıktı dosyası
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "ataturk_data.txt")


def _temizle(metin: str) -> str:
    """Metni temizler: fazla boşluk, satır sonları, Wikipedia referansları."""
    if not metin or not metin.strip():
        return ""
    # Wikipedia [1], [2] referanslarını kaldır
    metin = re.sub(r"\[\d+\]", "", metin)
    # Fazla boşluk ve satır sonlarını tek boşluğa indir
    metin = re.sub(r"\s+", " ", metin)
    return metin.strip()


def _fetch(url: str) -> Optional[str]:
    """URL'den HTML içeriğini döndürür. Hata durumunda None."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except Exception as e:
        print(f"  Hata ({url}): {e}")
        return None


def scrape_wikipedia(html: str) -> str:
    """Wikipedia HTML'inden ana metin içeriğini çıkarır."""
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", id="mw-content-text")
    if not content:
        return ""

    # Script, style, nav, reflist vb. kaldır
    for tag in content.find_all(["script", "style", "nav", "sup", "table"]):
        tag.decompose()

    paragraflar = []
    for el in content.find_all(["p", "li", "h2", "h3"]):
        text = el.get_text(separator=" ", strip=True)
        text = _temizle(text)
        if text and len(text) > 20:
            paragraflar.append(text)

    return "\n\n".join(paragraflar)


def scrape_ataturk_net(html: str) -> str:
    """ataturk.net HTML'inden metin içeriğini çıkarır."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["script", "style", "nav", "header", "footer", "form"]):
        tag.decompose()

    body = soup.find("body") or soup
    text = body.get_text(separator=" ", strip=True)
    text = _temizle(text)
    # Çok kısa satırları ve tekrarları azalt
    satirlar = [s.strip() for s in text.split(".") if len(s.strip()) > 30]
    return "\n\n".join(satirlar) if satirlar else text


def run():
    """Tüm kaynaklardan veriyi çeker, birleştirir ve dosyaya yazar."""
    os.makedirs(DATA_DIR, exist_ok=True)
    bolumler = []

    # 1. Türkçe Wikipedia
    print("Türkçe Wikipedia çekiliyor...")
    html = _fetch(WIKIPEDIA_URL)
    if html:
        wiki_metin = scrape_wikipedia(html)
        if wiki_metin:
            bolumler.append("=== Kaynak: Türkçe Wikipedia (Mustafa Kemal Atatürk) ===\n\n" + wiki_metin)
            print("  Tamamlandı.")

    # 2. ataturk.net
    print("ataturk.net çekiliyor...")
    html = _fetch(ATATURK_NET_URL)
    if html:
        net_metin = scrape_ataturk_net(html)
        if net_metin:
            bolumler.append("=== Kaynak: ataturk.net ===\n\n" + net_metin)
            print("  Tamamlandı.")

    if not bolumler:
        print("Hiç metin çekilemedi.")
        return

    birlesik = "\n\n".join(bolumler)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(birlesik)

    print(f"Veriler '{OUTPUT_FILE}' dosyasına yazıldı.")


if __name__ == "__main__":
    run()
