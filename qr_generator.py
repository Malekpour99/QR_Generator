import os
import qrcode
import pandas as pd
from PIL import Image
from dataclasses import dataclass


@dataclass
class QRCodeConfig:
    """
    Configuration settings for QR code generation.

    version: Controls the overall size (1 = 21x21, higher = larger QR)
    error_correction: error correction level
    box_size: Size of each box (increase for larger QR)
    border: Border thickness (default is 4)
    """

    version: int
    error_correction: int
    box_size: int
    border: int
    fill_color: str
    back_color: str


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


def generate_qr_codes_for_csv(
    csv_file: str,
    output_dir: str,
    qr_config: QRCodeConfig,
    skip_rows: int = 1,
    name_column_index: int = 0,
    data_column_index: int = 1,
) -> None:
    """
    Generate QR codes for data in a CSV file.

    Args:
        csv_file: Path to the CSV file
        output_dir: Directory to save the QR codes
        qr_config: Configuration for QR code generation
        skip_rows: Number of rows to skip in the CSV file
        name_column_index: Column index containing names for files
        data_column_index: Column index containing QR code data
    """
    # Initialize services
    data_reader = CSVDataReader()
    file_system = FileSystem()
    qr_generator = QRCodeGenerator(qr_config)

    # Create output directory
    file_system.create_directory(output_dir)

    # Read data
    df = data_reader.read_file(csv_file, skip_rows)

    # Generate QR codes
    for index, row in df.iterrows():
        data = str(row[data_column_index])
        name = str(row[name_column_index])

        qr_image = qr_generator.generate(data)

        # Save QR code
        qr_path = os.path.join(output_dir, f"{index+1}-{name}.png")
        file_system.save_image(qr_image, qr_path)

    print("QR codes generated successfully!")


def main():
    # Configuration
    csv_file = "list.csv"
    output_dir = "QR_codes"

    qr_config = QRCodeConfig(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction
        box_size=10,
        border=4,
        fill_color="black",
        back_color="white",
    )

    # Generate QR codes
    generate_qr_codes_for_csv(csv_file, output_dir, qr_config)


if __name__ == "__main__":
    main()
