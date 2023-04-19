""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import date
import os
import image_lib
import inspect
from sys import argv, exit
import sqlite3
import requests
import apod_api
import hashlib
NASA_API_URL = 'https://api.nasa.gov/planetary/apod'
NASA_API_KEY = 'eoUZeSrhO562HTqLJZYFiGrcQt6QDFV5BvY2wp5h'
PICTURE_OF_THE_DAY = 'https://apod.nasa.gov/apod/image/2303/MayanMilkyWay_Fernandez_1600.jpg'

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)


    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    apod_date_str = argv[1] if len(argv) > 1 else None
    if apod_date_str:
        try:
            apod_date = date.fromisoformat(argv[1])
        except:
                if apod_date > date.today():
                    print('Error: APOD date cannot be in the future')
                    exit()
                elif apod_date < date.fromisoformat('1995-06-16'):
                    print('No data from before this date')
                    exit()
        else:
                print(f'Error: Invalid date format')
                exit()
    else:
        apod_date = date.today()



    
    return apod_date


def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir
    global image_cache_db
    # Determine the path of the image cache directory
    script_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(script_path)
    image_cache_dir = os.path.join(parent_dir, 'images')
    print(f'Image cache directory: {image_cache_dir}')
    # Created the image cache directory if it does not already exist
    if not os.path.isdir(image_cache_dir):
        os.makedirs(image_cache_dir)
        print(f'Image cache directory created.')
    else:
        print(f'Image cache directory already exists.')
    # Determine the path of image cache DB
    image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')
    print(f'Image cache DB: {image_cache_db}')
    # Create the DB if it does not already exist
    if not os.path.isdir(image_cache_db):
        conn = sqlite3.connect(image_cache_db)
        cur = conn.cursor()
        apod_info_query = """
            CREATE TABLE IF NOT EXISTS image_cache
            (
                id              INTEGER PRIMARY KEY,
                title           TEXT NOT NULL,
                explanation     TEXT NOT NULL,
                full_path       TEXT NOT NULL,
                sha256          TEXT NOT NULL
            )
        """
        cur.execute(apod_info_query)
        conn.commit()
        conn.close()
        print('Image cache DB created.')
    else:
        print('Image cache DB already exists.')
    

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date.isoformat())
    # Download the APOD information from the NASA API
    apod_info = apod_api.get_apod_info(apod_date)

    # Download the APOD image
    image_url = apod_info['hdurl']
    print(f'APOD URL: {image_url}')
    image_bytes = image_lib.download_image(image_url)

    # Check whether the APOD already exists in the image cache
    if image_bytes is None:
        return
    
    # Save the APOD file to the image cache directory
    image_title = apod_info['title']
    image_path = determine_apod_file_path(image_title, image_url)
    file_ext = image_url.split('.')[-1]
    image_path = os.path.join(image_cache_dir, f'{image_title}.{file_ext}')
    image_lib.save_image_file(image_bytes, image_path)
    
    
    # Add the APOD information to the DB
    conn = sqlite3.connect(image_cache_db)
    cur = conn.cursor()
    apod_query_info = """
        INSERT INTO image_cache
        (
            id  
        )
        VALUES(?);
    """

    
    conn.commit()
    conn.close()

    return 0

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    conn = sqlite3.connect(image_cache_db)
    cur = conn.cursor()
    apod_info_query = """
        INSERT INTO image_cache
        (
            title,
            explanation,
            full_path,
            sha256
        )
        VALUES(?, ?, ?, ?);
    """

    apod_info = apod_api.get_apod_info()
    title = apod_info['title']
    explanation = apod_info['explanation']
    file_path = os.path.join(image_cache_dir)
    sha256 = hashlib.sha256(apod_info['hdurl']).hexdigest()
    values = (title, explanation, file_path, sha256)
    
    cur.execute(apod_info_query, values)
    conn.commit()
    conn.close()
    return 0

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    
    apod_info = apod_api.get_apod_info()
    image_sha256 = hashlib.sha256(apod_info['hdurl']).hexdigest()
    if image_sha256 == image_cache_db['sha256']:
        print(f'APOD SHA-256: {image_sha256}')
        print('APOD image already exists')
        return image_cache_db['id']
    else:
        print(f'APOD SHA-256: {image_sha256}')

    return 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    apod_date = get_apod_date()
    apod_info = apod_api.get_apod_info(apod_date)
    image_url = apod_info['hdurl']
    image_title = apod_info['title']
    file_ext = image_url.split('.')[-1]
    image_path = os.path.join(image_cache_dir, f'{image_title}.{file_ext}')
    print(f'APOD file path: {image_path}')
    return

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # Query DB for image info
    conn = sqlite3.connect(image_cache_db)
    cur = conn.cursor()
    query_params = """
        SELECT id, title, explanation, full_path FROM image_cache;
    """
    
    cur.execute(query_params)
    query = cur.fetchall()
    
    conn.close()
    
    # Put information into a dictionary
    apod_info = {
        'title': query, 
        'explanation': query,
        'file_path': query,
    }
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    
    resp_msg = requests.get(NASA_API_URL)
    if resp_msg.status_code == requests.codes.ok:
        apod_dict = resp_msg.json()
        apod_title_list = [t['title'] for t in apod_dict]
        return apod_title_list

    # This function is only needed to support the APOD viewer GUI
    return

if __name__ == '__main__':
    main()







