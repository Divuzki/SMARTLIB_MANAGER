# qr_module.py
import qrcode
from PIL import Image

def generate_qr(data, output_file="qr.png"):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_file)
    return output_file
