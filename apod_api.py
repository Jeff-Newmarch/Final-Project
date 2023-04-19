'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests
from datetime import date
from sys import argv
import os


NASA_API_URL = 'https://api.nasa.gov/planetary/apod'
NASA_API_KEY = 'eoUZeSrhO562HTqLJZYFiGrcQt6QDFV5BvY2wp5h'

def main():
    
    apod_date = date.fromisoformat('2022-05-09')
    apod_dict = get_apod_info(apod_date)
    get_apod_image_url(apod_dict)
    

    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    query_params = {
        'api_key': NASA_API_KEY,
        'date': apod_date,
        'thumbs': True
    }
    
    print(f'Getting {apod_date} APOD information from NASA...', end='')
    resp_msg = requests.get(NASA_API_URL, params=query_params)

    if resp_msg.ok:
        print('success')
        apod_info = resp_msg.json()
        return apod_info
    else:
        print('failure')
        print(f'Response code: {resp_msg.status_code} ({resp_msg.reason})')
    
      

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    apod_info_dict = {
        'api_key': NASA_API_KEY,
        'thumbs': True
    }
    resp_msg = requests.get(NASA_API_URL, params=apod_info_dict)
    if resp_msg.ok:
        print('success')
        apod_info_dict = resp_msg.json()
        return apod_info_dict
    else:
        print('failure')
        print(f'Response code: {resp_msg.status_code} ({resp_msg.reason})')
    if apod_info_dict['media_type'] == 'image':
        image_url = apod_info_dict['hdurl']
        print(f'APOD URL: {image_url}')
    if apod_info_dict['media_type'] == 'video':
        video_url = apod_info_dict['thumbnail_url']
        print(f'APOD URL: {video_url}')
    
    return apod_info_dict

if __name__ == '__main__':
    main()