from flask import Flask, Response, request, jsonify
import requests
import tempfile
import os


def extract_file_id(share_link):
    """Extract file ID from Google Drive share link"""
    try:
        if '/d/' in share_link:
            file_id = share_link.split('/d/')[1].split('/')[0]
        elif 'id=' in share_link:
            file_id = share_link.split('id=')[1].split('&')[0]
        else:
            return None
        return file_id
    except:
        return None

def get_direct_download_link(file_id):
    """Convert file ID to direct download link"""
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def download_video_from_gdrive(share_link, save_path=None):
    """Download video from Google Drive share link"""
    file_id = extract_file_id(share_link)
    if not file_id:
        return None, "Invalid Google Drive link"
    
    direct_link = get_direct_download_link(file_id)
    
    try:
        response = requests.get(direct_link, stream=True)
        response.raise_for_status()
        
        # If no save path provided, create temporary file
        if save_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            save_path = temp_file.name
            temp_file.close()
        
        # Download and save the video
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return save_path, "Success"
    
    except requests.exceptions.RequestException as e:
        return None, f"Download error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_video_stream(share_link):
    """Get video as a streaming response"""
    file_id = extract_file_id(share_link)
    if not file_id:
        return None
    
    direct_link = get_direct_download_link(file_id)
    
    try:
        response = requests.get(direct_link, stream=True)
        response.raise_for_status()
        return response
    except:
        return None



