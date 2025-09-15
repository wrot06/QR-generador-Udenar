from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import qrcode
from PIL import Image, ImageEnhance, ImageOps
import io

app = FastAPI()

@app.get("/generate-qr/")
def generate_qr(data: str = Query(..., description="Texto o URL para el QR")):
    # Generar QR con buena resolución
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,  # tamaño de cada "cuadradito"
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Insertar logo (logo.png debe estar en la misma carpeta que main.py)
    try:
        logo = Image.open("logo.png")

        # Ajustar tamaño del logo (máx. 30% del QR)
        qr_size = img.size[0]
        logo_size = qr_size // 4  # 25% del QR
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        # Mejorar brillo y contraste
        logo = ImageEnhance.Brightness(logo).enhance(1.2)
        logo = ImageEnhance.Contrast(logo).enhance(1.2)

        # Agregar borde blanco alrededor del logo
        logo = ImageOps.expand(logo, border=10, fill="white")

        # Posición centrada
        pos = (
            (img.size[0] - logo.size[0]) // 2,
            (img.size[1] - logo.size[1]) // 2,
        )

        img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)

    except FileNotFoundError:
        pass  # Si no hay logo.png, genera el QR normal

    # Devolver la imagen
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
