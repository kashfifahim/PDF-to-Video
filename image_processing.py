import cv2
import os
import re
import zipfile


def extract_images_from_zip(zip_path, extract_to):
    """
    Extract all files from a ZIP archive to a specified directory.

    This function opens a ZIP file located at `zip_path` and extracts its contents
    into the directory specified by `extract_to`. The function does not return any value.

    Parameters:
    zip_path (str): The path to the ZIP file that needs to be extracted.
    extract_to (str): The path of the directory where the contents of the ZIP file will be extracted.

    Returns:
    str or None: The path of the folder with the same name as the zip file containing image files, or None if no such folder is found.

    Example:
    >>> folder_path = extract_images_from_zip('path/to/zipfile.zip', 'path/to/destination/directory')
    >>> print(folder_path)
    """
    print(f"Extracting images from {zip_path} to {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return find_folder_with_images(extract_to)


def find_folder_with_images(extract_to):
    """
    Traverse a directory to find the first subfolder containing image files.
    This function walks through all the subdirectories starting from the given directory
    (`extract_to`). It checks each file to see if it is an image file (specifically, with
    extensions .png, .jpg, .jpeg). Once it finds a folder containing at least one image file,
    it prints the folder's path and returns it. If no such folder is found, the function prints
    a message indicating that no folder with images was found and returns None.
    Parameters:
    extract_to (str): The path of the directory to start the search from.
    Returns:
    str or None: The path of the first folder containing image files, or None if no such folder is found.
    Example:
    >>> folder_path = find_folder_with_images('/path/to/search')
    >>> print(folder_path)
    """

    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                print(f"Images found in folder: {root}")
                return root
    print("No folder with images found.")
    return None


def natural_sort_key(s):
    """
    Generate a key for sorting strings that contain numerical values in a natural way.

    This function is useful for sorting strings that contain numbers, where the numerical
    part of the strings should be interpreted based on its numerical value rather than
    alphabetical ordering. For example, it ensures '2' comes before '10'.

    Parameters:
    s (str): The string to be transformed into a sort key.

    Returns:
    list: A list containing a mix of integers and strings, derived from the input string.
          The integers are used for numerical comparison, and the strings are used for
          standard alphabetical comparison.

    Example:
    >>> sorted(['item2', 'item12', 'item1'], key=natural_sort_key)
    ['item1', 'item2', 'item12']
    """

    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def resize_image(image, target_width, target_height):
    """
    Resize an image to fit within the specified dimensions while maintaining the original aspect ratio.
    If the resized image does not match the target dimensions, it is padded with black color to fill the gaps.

    The function calculates the new dimensions of the image based on the target dimensions while preserving
    the aspect ratio. If the new dimensions are smaller than the target dimensions in either width or height,
    the image is padded with black color on the top/bottom or left/right respectively.

    Parameters:
    image (ndarray): The image to be resized, represented as a NumPy array.
    target_width (int): The desired width of the image after resizing and padding.
    target_height (int): The desired height of the image after resizing and padding.

    Returns:
    ndarray: The resized and padded image as a NumPy array.

    Note:
    This function requires OpenCV (cv2) for image processing.

    Example:
    >>> img = cv2.imread('path/to/image.jpg')
    >>> resized_img = resize_image(img, 800, 600)
    >>> cv2.imshow('Resized Image', resized_img)
    >>> cv2.waitKey(0)
    >>> cv2.destroyAllWindows()
    """
    original_height, original_width = image.shape[:2]
    aspect_ratio = original_width / original_height
    
    if original_width > original_height:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * aspect_ratio)

    resized_image = cv2.resize(image, (new_width, new_height))
    
    # If the new dimensions are smaller in any direction, pad the resized image with black color
    top_padding = (target_height - new_height) // 2
    bottom_padding = target_height - new_height - top_padding
    left_padding = (target_width - new_width) // 2
    right_padding = target_width - new_width - left_padding

    return cv2.copyMakeBorder(resized_image, top_padding, bottom_padding, left_padding, right_padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])


def images_to_video(image_paths, output_video_file, fps=30, duration=5, target_width=1920, target_height=1080):
    """
    Convert a set of images into a video file. Each image is resized to fit the specified target dimensions
    and is repeated in the video for a specified duration and frame rate.

    This function creates a video by looping over each image in the given list of image paths. Each image
    is resized to the target dimensions using the `resize_image` function. The image is then duplicated 
    across multiple frames to achieve the desired duration and frame rate in the final video.

    Parameters:
    image_paths (list of str): A list containing the file paths of the images to be included in the video.
    output_video_file (str): The file path where the output video will be saved.
    fps (int, optional): Frames per second in the output video. Default is 30.
    duration (int, optional): Duration (in seconds) to display each image in the video. Default is 5.
    target_width (int, optional): The target width of the video (and hence the resized images). Default is 1920.
    target_height (int, optional): The target height of the video (and hence the resized images). Default is 1080.

    Returns:
    None: The function does not return anything but saves the generated video at `output_video_file`.

    Example:
    >>> images_to_video(['image1.jpg', 'image2.jpg'], 'output.mp4', fps=24, duration=3, target_width=1280, target_height=720)
    """

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_file, fourcc, fps, (target_width, target_height))
    
    for img_path in image_paths:
        img = cv2.imread(img_path)
        resized_img = resize_image(img, target_width, target_height)
        
        for _ in range(fps * duration):
            out.write(resized_img)
    
    out.release()