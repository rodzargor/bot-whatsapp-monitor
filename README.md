# Bot WhatsApp — Monitor de Mercado

Bot que monitorea activos bursátiles en tiempo real y envía alertas por WhatsApp cuando un activo supera umbrales de caída configurados.

## ¿Qué hace?

- Monitorea precios de acciones (NYSE, NASDAQ, BME) cada 60 segundos usando `yfinance`
- Detecta caídas por niveles (n1, n2, n3) según el tipo de activo
- Envía alertas instantáneas por WhatsApp vía Twilio
- Incluye análisis automático con IA (OpenRouter / GPT-4o-mini) y resumen de noticias relevantes

## Archivos

| Archivo | Descripción |
|---|---|
| `monitor.py` | Bucle principal de monitoreo de activos |
| `app.py` | Servidor Flask: recibe alertas y responde comandos por WhatsApp |
| `estado_mercado.json` | Estado actual del mercado (generado automáticamente) |
| `claves.env` | Variables de entorno con credenciales (no incluido en el repo) |

## Configuración

Crea un archivo `claves.env` con estas variables:

```
ACCOUNT_SID=tu_twilio_sid
AUTH_TOKEN=tu_twilio_token
FROM_WHATSAPP=whatsapp:+14155238886
TO_WHATSAPP=whatsapp:+34XXXXXXXXX
OPENROUTER_API_KEY=tu_clave_openrouter
```

## Uso

```bash
# Terminal 1 — servidor Flask
python app.py

# Terminal 2 — monitor de mercado
python monitor.py
```

## Niveles de alerta

| Nivel | Alta volatilidad | Media | Baja |
|---|---|---|---|
| n1 | -5% | -3% | -2% |
| n2 | -8% | -5% | -4% |
| n3 | -12% | -7% | -6% |
