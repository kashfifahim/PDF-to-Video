import fitz
import os
import zipfile
from pathlib import Path
from PyPDF2 import PdfReader
from pdf2image import convert_from_path


def pdf_to_images_mupdf(pdf_path, output_folder):
    # Check if output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # number of page
        pix = page.get_pixmap()
        output_image_path = os.path.join(output_folder, f'page_{page_num + 1}.png')
        pix.save(output_image_path)
    
    # Close the document
    doc.close()


def pdf_to_images(pdf_path, output_folder):
    # Check if output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Read the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
    
        # Convert each page to an image
        for page_number in range(num_pages):
            # Convert the current page to image
            images = convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)

            # Save the image
            for image in images:
                image.save(os.path.join(output_folder, f'page_{page_number + 1}.png'), 'PNG')


def zip_folder(folder_path, output_zip_file):
    # Create a ZipFile object in write mode
    with zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Create a relative path for files to keep the directory structure
                relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                # Add file to the zip file
                zipf.write(os.path.join(root, file), arcname=relative_path)