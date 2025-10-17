from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import qrcode
from PIL import Image, ImageEnhance, ImageOps
import io

app = FastAPI()

@app.get("/generate-qr/")
def generate_qr(data: str = Query(..., description="Texto o URL para el QR")):
    # Generar QR sin borde nativo
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Recortar fondo blanco sobrante
    bbox = img.getbbox()
    img = img.crop(bbox)

    # Insertar logo (opcional)
    try:
        logo = Image.open("logo.png").convert("RGBA")
        qr_size = img.size[0]
        logo_size = qr_size // 4
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        # Mejorar contraste y brillo del logo
        logo = ImageEnhance.Brightness(logo).enhance(1.2)
        logo = ImageEnhance.Contrast(logo).enhance(1.2)

        # Borde blanco alrededor del logo
        logo = ImageOps.expand(logo, border=2, fill="white")

        # Posición centrada
        pos = ((img.size[0] - logo.size[0]) // 2,
               (img.size[1] - logo.size[1]) // 2)

        img.paste(logo, pos, mask=logo)
    except FileNotFoundError:
        pass

    # ✅ Agregar borde blanco alrededor del QR completo (visible al descargar)
    borde_blanco = 40  # puedes ajustar el grosor aquí
    img = ImageOps.expand(img, border=borde_blanco, fill="white")

    # Devolver PNG
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
