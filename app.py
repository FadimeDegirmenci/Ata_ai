"""
Atatürk ile Sohbet - Gradio 6.6 uyumlu arayüz.
Sol: Atatürk görseli, Sağ: Sohbet alanı. Soru ve cevap farklı font stiliyle.
"""

import html
import os
import gradio as gr
from llm import ataturk_cevapla

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
ATATURK_IMAGE_PATH = os.path.join(ASSETS_DIR, "ataturk.jpg")
if not os.path.isfile(ATATURK_IMAGE_PATH):
    ATATURK_IMAGE_PATH = None


def _gecmisi_html_cevir(gecmis):
    """[(soru, cevap), ...] listesini stilli HTML'e çevirir. Arka plan siyah, yazılar beyaz."""
    wrap = "<div style='background:#000; color:#fff; padding:1rem; min-height:200px; border-radius:8px;'>"
    end = "</div>"
    if not gecmis:
        return wrap + "<p style='color:#ccc;'>Sohbet burada görünecek. Aşağıdan bir şey yazıp Gönder'e tıklayın.</p>" + end
    parts = []
    for soru, cevap in gecmis:
        s = html.escape(str(soru)).replace("\n", "<br>")
        c = html.escape(str(cevap)).replace("\n", "<br>")
        parts.append(
            f"<p style='margin-bottom:0.25em;'><strong style='font-weight:700; color:#fff;'>Siz:</strong> "
            f"<span style='font-weight:600; color:#e0e0e0;'>{s}</span></p>"
        )
        parts.append(
            f"<p style='margin-top:0.25em; margin-bottom:1em;'><strong style='font-weight:600; color:#fff;'>Atatürk:</strong> "
            f"<span style='font-weight:400; font-style:italic; color:#d0d0d0;'>{c}</span></p>"
        )
    return wrap + "\n".join(parts) + end


def yanit_ver(mesaj, sohbet_gecmisi):
    if not (mesaj and str(mesaj).strip()):
        return _gecmisi_html_cevir(sohbet_gecmisi), ""
    cevap = ataturk_cevapla(mesaj)
    sohbet_gecmisi.append((mesaj, cevap))
    return _gecmisi_html_cevir(sohbet_gecmisi), ""


with gr.Blocks(title="Atatürk ile Sohbet") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Image(
                value=ATATURK_IMAGE_PATH,
                type="filepath",
                height=320,
                show_label=False,
            )

        with gr.Column(scale=2):
            sohbet_alani = gr.HTML(
                value="<div style='background:#000; color:#fff; padding:1rem; min-height:200px; border-radius:8px;'><p style='color:#ccc;'>Sohbet burada görünecek. Aşağıdan bir şey yazıp Gönder'e tıklayın.</p></div>",
                label="Sohbet",
            )
            gecmis = gr.State(value=[])
            with gr.Row():
                kutu = gr.Textbox(
                    placeholder="Atatürk'e bir şey yazın...",
                    label="Mesajınız",
                    show_label=False,
                    scale=4,
                    container=False,
                )
                gonder = gr.Button("Gönder", variant="primary", scale=1, min_width=100)

    gonder.click(
        yanit_ver,
        inputs=[kutu, gecmis],
        outputs=[sohbet_alani, kutu],
    )
    kutu.submit(
        yanit_ver,
        inputs=[kutu, gecmis],
        outputs=[sohbet_alani, kutu],
    )

if __name__ == "__main__":
    demo.launch()
