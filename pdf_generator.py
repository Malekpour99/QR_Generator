import os
import qrcode
import pandas as pd
from PIL import Image
import arabic_reshaper
from typing import Tuple
from dataclasses import dataclass
from reportlab.pdfgen import canvas
from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont


@dataclass
class QRCodeConfig:
    """Configuration settings for QR code generation."""

    version: int
    error_correction: int
    box_size: int
    border: int
    fill_color: str
    back_color: str


@dataclass
class PDFConfig:
    """Configuration settings for PDF generation."""

    page_size: Tuple[int, int]
    background_image: str
    title_font: str
    title_font_size: int
    title_color: Tuple[float, float, float]
    number_font: str
    number_font_size: int
    number_color: Tuple[float, float, float]
    qr_size: int
    title_y_offset: int
    qr_y_offset: int
    number_y_offset: int


class FarsiTextProcessor:
    """Handles Farsi text processing for correct display."""

    @staticmethod
    def process_text(raw_text: str) -> str:
        """
        Process Farsi text for correct display.

        Args:
            raw_text: The raw Farsi text

        Returns:
            Correctly processed Farsi text
        """
        reshaped_text = arabic_reshaper.reshape(raw_text)
        return get_display(reshaped_text)


class QRCodeGenerator:
    """Class responsible for generating QR codes."""

    def __init__(self, config: QRCodeConfig):
        self.config = config

    def generate(self, data: str) -> Image:
        """
        Generate a QR code image for the given data.

        Args:
            data: The data to encode in the QR code

        Returns:
            A QR code image object
        """
        qr = qrcode.QRCode(
            version=self.config.version,
            error_correction=self.config.error_correction,
            box_size=self.config.box_size,
            border=self.config.border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        return qr.make_image(
            fill=self.config.fill_color, back_color=self.config.back_color
        )


class FileSystem:
    """Class for handling file system operations."""

    def create_directory(self, directory_path: str) -> None:
        """
        Create a directory if it doesn't exist.

        Args:
            directory_path: Path to the directory to create
        """
        os.makedirs(directory_path, exist_ok=True)

    def save_image(self, image, file_path: str) -> None:
        """
        Save an image to a file.

        Args:
            image: The image object to save
            file_path: Path where the image should be saved
        """
        image.save(file_path)


class CSVDataReader:
    """Class responsible for reading data from CSV files."""

    def read_file(self, file_path: str, skip_rows: int = 0) -> pd.DataFrame:
        """
        Read data from a CSV file.

        Args:
            file_path: Path to the CSV file
            skip_rows: Number of rows to skip at the beginning

        Returns:
            DataFrame containing the CSV data
        """
        return pd.read_csv(file_path, skiprows=skip_rows, header=None)


class PDFGenerator:
    """Class responsible for generating PDFs."""

    def __init__(self, config: PDFConfig):
        self.config = config

    def generate_pdf(
        self, output_path: str, name: str, number: str, qr_image_path: str
    ) -> None:
        """
        Generate a PDF with a name, number, and QR code.

        Args:
            output_path: Path where the PDF will be saved
            name: The name to display in the PDF
            number: The number to display in the PDF
            qr_image_path: Path to the QR code image
        """
        # Create PDF canvas with custom page size
        c = canvas.Canvas(output_path, pagesize=self.config.page_size)

        # Calculate center positions
        page_width, page_height = self.config.page_size
        x_center = page_width / 2
        y_position = page_height - 100

        # Draw background image
        c.drawImage(
            self.config.background_image, 0, 0, width=page_width, height=page_height
        )

        # Add name (title)
        c.setFont(self.config.title_font, self.config.title_font_size)
        c.setFillColorRGB(*self.config.title_color)
        c.drawCentredString(x_center, y_position - self.config.title_y_offset, name)

        # Add QR code
        qr_img = ImageReader(qr_image_path)
        qr_half_size = self.config.qr_size / 2
        c.drawImage(
            qr_img,
            x_center - qr_half_size,
            y_position - self.config.qr_size - self.config.qr_y_offset,
            self.config.qr_size,
            self.config.qr_size,
        )

        # Add number
        c.setFont(self.config.number_font, self.config.number_font_size)
        c.setFillColorRGB(*self.config.number_color)
        c.drawCentredString(
            x_center,
            y_position - self.config.qr_size - self.config.number_y_offset,
            number,
        )

        # Save the PDF
        c.save()


class FontManager:
    """Class for managing PDF fonts."""

    @staticmethod
    def register_font(font_name: str, font_path: str) -> None:
        """
        Register a font for use in PDFs.

        Args:
            font_name: The name to register the font under
            font_path: Path to the font file
        """
        pdfmetrics.registerFont(TTFont(font_name, font_path))


def process_records(
    csv_file: str,
    qr_dir: str,
    pdf_dir: str,
    qr_config: QRCodeConfig,
    pdf_config: PDFConfig,
    name_column_index: int = 0,
    number_column_index: int = 1,
    skip_rows: int = 1,
) -> None:
    """
    Process records from a CSV file to generate QR codes and PDFs.

    Args:
        csv_file: Path to the CSV file
        qr_dir: Directory to save QR codes
        pdf_dir: Directory to save PDFs
        qr_config: Configuration for QR code generation
        pdf_config: Configuration for PDF generation
        name_column_index: Index of the column containing names
        number_column_index: Index of the column containing numbers
        skip_rows: Number of rows to skip in the CSV file
    """
    # Initialize services
    file_system = FileSystem()
    csv_reader = CSVDataReader()
    qr_generator = QRCodeGenerator(qr_config)
    pdf_generator = PDFGenerator(pdf_config)
    text_processor = FarsiTextProcessor()

    # Create output directories
    file_system.create_directory(qr_dir)
    file_system.create_directory(pdf_dir)

    # Read CSV data
    df = csv_reader.read_file(csv_file, skip_rows)

    # Process each record
    for index, row in df.iterrows():
        raw_name = str(row[name_column_index])
        number = str(row[number_column_index])

        # Process Farsi text
        farsi_name = text_processor.process_text(raw_name)

        # Generate and save QR code
        qr_image = qr_generator.generate(number)
        qr_img_path = os.path.join(qr_dir, f"{index+1}-{raw_name}.png")
        file_system.save_image(qr_image, qr_img_path)

        # Generate PDF
        pdf_file = os.path.join(pdf_dir, f"{index+1}-{raw_name}.pdf")
        pdf_generator.generate_pdf(pdf_file, farsi_name, number, qr_img_path)

        print(f"PDF generated: {pdf_file}")

    print("All PDFs created successfully!")


def main():
    # Register Farsi font
    FontManager.register_font("BNazanin", "BNazanin.ttf")
    FontManager.register_font("Vazir-Bold", "Vazir-Bold.ttf")

    # Configuration
    csv_file = "list.csv"
    qr_dir = "QR_codes"
    pdf_dir = "PDF_files"

    qr_config = QRCodeConfig(
        version=8,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=12,
        border=4,
        fill_color="black",
        back_color="white",
    )

    pdf_config = PDFConfig(
        page_size=(225, 400),
        background_image="background.jpg",
        title_font="Vazir-Bold",
        title_font_size=20,
        title_color=(1, 1, 1),  # White
        number_font="Helvetica",
        number_font_size=14,
        number_color=(0, 0, 0),  # Black
        qr_size=150,
        title_y_offset=40,
        qr_y_offset=63,
        number_y_offset=70,
    )

    # Process records
    process_records(csv_file, qr_dir, pdf_dir, qr_config, pdf_config)


if __name__ == "__main__":
    main()
