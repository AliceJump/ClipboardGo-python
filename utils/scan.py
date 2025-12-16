from PIL import Image
from pyzbar.pyzbar import decode

def decode_qr(img: Image.Image) -> str:
    result = decode(img)
    return result[0].data.decode() if result else ""