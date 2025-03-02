import pandas as pd
import qrcode
import os

# Load CSV file
csv_file = "list.csv"
df = pd.read_csv(csv_file, skiprows=1, header=None)  # Skipping headers

# Create output directory for QR codes
output_dir = "qr_codes"
os.makedirs(output_dir, exist_ok=True)

for index, row in df.iterrows():
    number = str(row[1])  # Assuming the second column contains numbers
    
    # Create QRCode object with custom size [Total Size = (Version × 4 + 17) × Box Size]
    qr = qrcode.QRCode(
        version=3,  # Controls the overall size (1 = 21x21, higher = larger QR)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction
        box_size=10,  # Size of each box (increase for larger QR)
        border=4  # Border thickness (default is 4)
    )
    qr.add_data(number)
    qr.make(fit=True)

    # Generate QR code image
    img = qr.make_image(fill="black", back_color="white")
    
    # Save QR code as an image file
    qr_path = os.path.join(output_dir, f"{index+1}-{row[0]}.png")
    img.save(qr_path)

print("QR codes generated successfully!")
