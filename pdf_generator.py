import os
import pandas as pd
import qrcode
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Register Farsi Font
pdfmetrics.registerFont(TTFont("BNazanin", "BNazanin.ttf"))
farsi_font = "BNazanin"

# Custom page size for PDF files (width, height)
custom_page_size = (300, 400)

# Load CSV file
csv_file = "list.csv"
df = pd.read_csv(csv_file, skiprows=1, header=None)  # Skip header


# Create output directories
qr_dir = "QR_codes"
pdf_dir = "PDF_files"
os.makedirs(qr_dir, exist_ok=True)
os.makedirs(pdf_dir, exist_ok=True)


for index, row in df.iterrows():
    raw_name = str(row[0])  # Name (first column, in Farsi)
    number = str(row[1])  # Number (second column)

    # Fix Farsi text for correct display
    reshaped_text = arabic_reshaper.reshape(raw_name)  # Reshape letters
    farsi_name = get_display(reshaped_text)  # Apply RTL correction

    # Generate QR Code
    qr = qrcode.QRCode(
        version=3,  # 29x29 grid
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(number)
    qr.make(fit=True)

    # Save QR code image
    qr_img_path = os.path.join(qr_dir, f"{index+1}-{raw_name}.png")
    img = qr.make_image(fill="black", back_color="white")
    img.save(qr_img_path)

    # Create a separate PDF for each user
    pdf_file = os.path.join(pdf_dir, f"{index+1}-{raw_name}.pdf")
    c = canvas.Canvas(pdf_file, pagesize=custom_page_size)

    # Set font
    c.setFont(farsi_font, 16)

    # Center positioning
    page_width, page_height = custom_page_size
    x_center = page_width / 2
    y_position = page_height - 100

    # Add Farsi Name (Title)
    c.drawCentredString(x_center, y_position, farsi_name)

    # Add QR Code Image
    qr_size = 150  # QR code size
    qr_img = ImageReader(qr_img_path)
    c.drawImage(qr_img, x_center - (qr_size / 2), y_position - qr_size - 10, qr_size, qr_size)

    # Add Number Below QR Code
    c.setFont("Helvetica", 12)
    c.drawCentredString(x_center, y_position - qr_size - 30, number)

    # Save the PDF
    c.save()

    print(f"PDF generated: {pdf_file}")

print("All PDFs created successfully!")
