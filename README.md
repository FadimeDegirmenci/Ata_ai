# Atatürk AI — Historical Character Chatbot

A RAG-based chatbot that lets you have a real-time Turkish conversation with Mustafa Kemal Atatürk. Built for the CIF418 Generative AI course.

---

## How It Works

1. **Web Scraping** — Biographical data is collected from Turkish Wikipedia and ataturk.net
2. **Vector Database** — Text is chunked and indexed in ChromaDB
3. **RAG Pipeline** — Each user query retrieves the 3 most relevant chunks
4. **LLM** — Groq API (LLaMA 3.3 70B) responds in Atatürk's voice
5. **UI** — Gradio web interface with Atatürk's portrait

---

## Setup

### 1. Install dependencies
```bash
pip install gradio requests beautifulsoup4 chromadb sentence-transformers groq python-dotenv
```

### 2. Add your API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_api_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

### 3. Scrape data
```bash
python scraper.py
```

### 4. Build vector database
```bash
python vector_db.py
```

### 5. Run the app
```bash
python app.py
```

Open `http://127.0.0.1:7860` in your browser.

---

## Project Structure

```
ataturk-ai/
├── app.py          # Gradio web interface
├── scraper.py      # Web scraping module
├── vector_db.py    # ChromaDB operations
├── llm.py          # Groq LLM integration
├── data/
│   └── ataturk_data.txt
├── assets/
│   └── ataturk.jpg
└── .env            # API key (not committed)
```

---

## Tech Stack

| Component | Tool |
|-----------|------|
| UI | Gradio |
| Scraping | BeautifulSoup4 |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |
| LLM | Groq API (LLaMA 3.3 70B) |

---

> ⚠️ This chatbot is for educational purposes only. Responses are AI-generated and may not accurately reflect Atatürk's views.
