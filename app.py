from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
import json
import yfinance as yf
from newspaper import Article
import os
from dotenv import load_dotenv

# ==========================================================
# 🔑 CARGAR VARIABLES
# ==========================================================

load_dotenv("claves.env")

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ==========================================================
# 📩 ENVÍO SEGURO WHATSAPP
# ==========================================================

def enviar_whatsapp(mensaje):
    try:
        # cortar por si acaso (extra seguridad)
        if len(mensaje) > 1500:
            mensaje = mensaje[:1500]

        client.messages.create(
            from_=FROM_WHATSAPP,
            body=mensaje,
            to=TO_WHATSAPP
        )
        print("✅ WhatsApp enviado")

    except Exception as e:
        print("❌ Error enviando WhatsApp:", e)

# ==========================================================
# 📊 ESTADO
# ==========================================================

def obtener_estado_mercado():
    try:
        with open("estado_mercado.json", "r") as f:
            data = json.load(f)

        mensaje = "📊 Estado actual:\n\n"

        for ticker, valores in data.items():
            mensaje += (
                f"{ticker}\n"
                f"Intradía: {valores['intradia']}%\n"
                f"Diario: {valores['diaria']}%\n\n"
            )

        return mensaje

    except:
        return "⚠️ No hay datos disponibles."

# ==========================================================
# 📰 NOTICIAS (RESUMIDAS)
# ==========================================================

def obtener_noticias_detalladas(ticker):
    try:
        data = yf.Ticker(ticker)
        noticias = data.news

        textos = []

        for noticia in noticias[:1]:  # 🔥 SOLO 1 noticia (clave)
            url = noticia.get("link", "")

            try:
                article = Article(url)
                article.download()
                article.parse()

                textos.append(article.text[:500])  # 🔥 LIMITAMOS

            except:
                continue

        return "\n\n".join(textos)

    except:
        return ""

# ==========================================================
# 🧠 IA
# ==========================================================

def analizar_movimiento(ticker, mensaje, noticias):
    prompt = f"""
Eres un analista financiero profesional.

Ticker: {ticker}

Movimiento:
{mensaje}

Noticias:
{noticias if noticias else "NO HAY NOTICIAS"}

Analiza:
- causa real o contexto
- si es técnico o fundamental
- si es rotación de capital

No inventes datos, pero razona como inversor.
"""

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=10
        )

        return response.json()["choices"][0]["message"]["content"]

    except:
        return "No se ha podido generar análisis."

# ==========================================================
# 📥 WEBHOOK
# ==========================================================

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '')

    if "estado" in incoming_msg.lower():
        reply = obtener_estado_mercado()
    else:
        reply = "Comando no reconocido."

    resp = MessagingResponse()
    resp.message(reply)

    return str(resp)

# ==========================================================
# 🚨 ALERTA (DIVIDIDA)
# ==========================================================

@app.route("/alerta", methods=["POST"])
def alerta():
    data = request.json
    mensaje = data.get("mensaje", "")

    print("🚨 ALERTA RECIBIDA:", mensaje)

    ticker = mensaje.split("\n")[0].replace("🚨 ", "").strip()

    # 1️⃣ ALERTA INMEDIATA
    enviar_whatsapp(mensaje)

    # 2️⃣ ANÁLISIS (después)
    noticias = obtener_noticias_detalladas(ticker)
    analisis = analizar_movimiento(ticker, mensaje, noticias)

    mensaje_analisis = f"🧠 {ticker}\n\n{analisis}"

    enviar_whatsapp(mensaje_analisis)

    return "ok"

# ==========================================================
# ▶️ START
# ==========================================================

if __name__ == "__main__":
    app.run(port=5000)