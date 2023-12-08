import json
from os import getenv
from pathlib import Path
import os
import shutil
from image_processing import images_to_video, natural_sort_key
from pdf_processing import pdf_to_images, pdf_to_images_mupdf

if __name__ == '__main__':
    print("Script started")
    # Section 1: Setting up the environment variables
    # Setting up input and output folders
    input_folder = Path(getenv('CROSSCOMPUTE_INPUT_FOLDER', 'batches/standard/input'))
    output_folder = Path(getenv('CROSSCOMPUTE_OUTPUT_FOLDER', 'batches/standard/output'))
    print(f"Input folder: {input_folder}, Output folder: {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)

    # Creating temporary folders for processing
    temp_folder = output_folder / 'temp'
    print(f"Temporary folder: {temp_folder}")
    temp_folder.mkdir(exist_ok=True)
    temp_video_file = temp_folder / 'temp_output_video.mp4'

    extract_to_folder = temp_folder / 'extracted_images'
    extract_to_folder.mkdir(exist_ok=True)
    
    # Load input variable for duration from input folder
    with (input_folder / 'variables.dictionary').open('rt') as f:
        variables = json.load(f)

    # PDF Processing
    pdf_files = list(input_folder.glob('*.pdf'))
    if not pdf_files:
        raise ValueError("No PDF file found in the input folder")
    pdf_file = pdf_files[0]
    print(f"PDF file found: {pdf_file}")
    pdf_to_images_mupdf(pdf_file, extract_to_folder)
    
    # # Finding the first zip file in the input folder
    # zip_files = list(input_folder.glob('*.zip'))
    # if not zip_files:
    #     print("No zip file found in the input folder")
    #     raise ValueError("No zip file found in the input folder")
    # zip_file_path = zip_files[0]
    # print(f"Zip file found: {zip_file_path}")

    # # Extracting images from the zip file and finding the folder with images
    # images_folder = extract_images_from_zip(zip_file_path, extract_to_folder)
    # if not images_folder:
    #     raise ValueError("No folder containing images was found")

    # Sorting the image paths
    image_paths = sorted([str(file_path) for file_path in extract_to_folder.glob('*.png')], key=natural_sort_key)

    # Setting the path for the output video file
    output_video_file = Path(output_folder / 'output_video.mp4')
    print(f"Output video file will be saved as: {output_video_file}")
    
    # duration from user here then pass it into the next function
    try:
        user_defined_duration = int(variables['duration'])
        if user_defined_duration <= 0:
            user_defined_duration = 5
    except ValueError:
        # If it's not an integer, set it to 5
        user_defined_duration = 5
    
    # Creating the video from images
    images_to_video(image_paths, str(temp_video_file), fps=30, duration=user_defined_duration)
    

    # Verifying the video creation and performing cleanup
    if os.path.exists(temp_video_file) and os.path.getsize(temp_video_file) > 0:
        print(f"Video file created successfully: {temp_video_file}")
        # Move the completed video to the output folder
        shutil.move(str(temp_video_file), str(output_video_file))
        print(f"Video moved to output folder: {output_video_file}")
        
        # Cleanup: delete the folder with extracted images
        try:
            shutil.rmtree(temp_video_file.parent)
            print(f"Deleted temp images folder: {extract_to_folder}")
        except OSError as e:
            print(f"Error deleting folder {extract_to_folder}: {e.strerror}")
    else:
        print(f"Video creation failed or video file is empty: {output_video_file}")

    print("Script ended")