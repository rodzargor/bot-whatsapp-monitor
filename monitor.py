import yfinance as yf
import time
import requests  # 👉 Para enviar alertas al servidor Flask
import json


# ==========================================================
# 🔥 NIVELES POR TIPO DE ACTIVO
# ==========================================================

NIVELES_ALTA = {"n1": -5, "n2": -8, "n3": -12}
#NIVELES_ALTA = {"n1": -1, "n2": -4, "n3": -6}
NIVELES_MEDIA = {"n1": -3, "n2": -5, "n3": -7}
NIVELES_BAJA = {"n1": -2, "n2": -4, "n3": -6}


# ==========================================================
# 📊 LISTA DE ACTIVOS
# ==========================================================

activos = {
    "RKLB": NIVELES_ALTA,
    "PLTR": NIVELES_ALTA,
    "ASTS": NIVELES_ALTA,
    "NVDA": NIVELES_ALTA,
    "EZE.MC": NIVELES_ALTA,
    "OHLA.MC": NIVELES_ALTA,

    "GOOGL": NIVELES_MEDIA,
    "META": NIVELES_MEDIA,
    "AAPL": NIVELES_MEDIA,
    "ASML": NIVELES_MEDIA,
    "ITX.MC": NIVELES_MEDIA,
    "FER.MC": NIVELES_MEDIA,
    "STLA": NIVELES_MEDIA,
    "RTX": NIVELES_MEDIA,
    "PFE": NIVELES_MEDIA,
    "LNG": NIVELES_MEDIA,

    "KO": NIVELES_BAJA,
    "COST": NIVELES_BAJA,
    "BRK-B": NIVELES_BAJA,
    "V": NIVELES_BAJA,
    "XOM": NIVELES_BAJA,
    "CVX": NIVELES_BAJA,
}


# ==========================================================
# 🧠 MEMORIA DE ESTADO (CLAVE)
# ==========================================================
# Guarda en qué nivel estaba cada activo anteriormente

estado_anterior = {}


# ==========================================================
# 📉 FUNCIÓN: VARIACIÓN INTRADÍA
# ==========================================================

def obtener_variacion_intradia(ticker):
    data = yf.Ticker(ticker)

    hist = data.history(period="1d", interval="1m", prepost=False)

    apertura = hist["Close"].iloc[0]
    precio_actual = hist["Close"].iloc[-1]

    cambio = ((precio_actual - apertura) / apertura) * 100

    return cambio


# ==========================================================
# 📊 FUNCIÓN: VARIACIÓN DIARIA (CIERRE AYER)
# ==========================================================

def obtener_variacion_diaria(ticker):
    data = yf.Ticker(ticker)

    intraday = data.history(period="1d", interval="1m", prepost=False)
    precio_actual = intraday["Close"].iloc[-1]

    diario = data.history(period="5d")
    cierre_ayer = diario["Close"].iloc[-2]

    cambio = ((precio_actual - cierre_ayer) / cierre_ayer) * 100

    return cambio


# ==========================================================
# 🧠 FUNCIÓN: DETERMINAR NIVEL
# ==========================================================

def obtener_nivel(cambio, niveles):
    if cambio <= niveles["n3"]:
        return "n3"
    elif cambio <= niveles["n2"]:
        return "n2"
    elif cambio <= niveles["n1"]:
        return "n1"
    else:
        return "normal"


# ==========================================================
# 📩 FUNCIÓN: ENVIAR ALERTA A FLASK
# ==========================================================

def enviar_alerta(mensaje):
    try:
        print("ENVIANDO ALERTA A FLASK...")
        requests.post(
            "http://localhost:5000/alerta",
            json={"mensaje": mensaje}
        )
    except Exception as e:
        print(f"Error enviando alerta: {e}")


print("\n--- MONITOREANDO MERCADO ---\n")


# ==========================================================
# 🔁 BUCLE PRINCIPAL
# ==========================================================

while True:

    for ticker, niveles in activos.items():

        try:
            # 🔥 Obtener datos
            cambio_intradia = obtener_variacion_intradia(ticker)
            cambio_diaria = obtener_variacion_diaria(ticker)

            print(f"{ticker}: Intradía {cambio_intradia:.2f}% | Diario {cambio_diaria:.2f}%")

            # 🔥 Detectar nivel actual
            nivel_actual = obtener_nivel(cambio_intradia, niveles)

            # 🔥 Obtener nivel anterior (si no existe → normal)
            nivel_previo = estado_anterior.get(ticker, "normal")

            # ==================================================
            # 🚨 SOLO SI CAMBIA EL NIVEL → ALERTA
            # ==================================================
            if nivel_actual != nivel_previo:

                mensaje = (
                    f"🚨 {ticker}\n"
                    f"Intradía: {cambio_intradia:.2f}%\n"
                    f"Diario: {cambio_diaria:.2f}%\n"
                    f"Cambio: {nivel_previo} → {nivel_actual}"
                )

                print(f"\n{mensaje}\n")

                # 📩 Enviar a WhatsApp (vía Flask)
                enviar_alerta(mensaje)

                # 🔥 Actualizar estado
                estado_anterior[ticker] = nivel_actual

        except Exception as e:
            print(f"Error con {ticker}: {e}")

    print("\n-----------------------------\n")

    # ==========================================================
    # 💾 GUARDAR ESTADO DEL MERCADO
    # ==========================================================

    estado_actual = {}

    for ticker, niveles in activos.items():
        try:
            cambio_intradia = obtener_variacion_intradia(ticker)
            cambio_diaria = obtener_variacion_diaria(ticker)

            estado_actual[ticker] = {
                "intradia": round(cambio_intradia, 2),
                "diaria": round(cambio_diaria, 2)
            }

        except:
            continue

    # Guardamos en archivo
    with open("estado_mercado.json", "w") as f:
        json.dump(estado_actual, f)

    time.sleep(60)