from flask import Flask, Response, request, jsonify
import requests
import tempfile
import os
import subprocess
import shutil
import base64
import json
from video_load import download_video_from_gdrive, get_video_stream
from ffmpeg_run_and_encode import process_video_with_ffmpeg, encode_frames_to_base64
from download_and_process import download_and_process_video

app = Flask(__name__)

def cleanup_temp_files(paths):
    """Clean up temporary files and directories"""
    for path in paths:
        try:
            if os.path.isfile(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            print(f"Error cleaning up {path}: {e}")

@app.route('/process_for_make', methods=['POST'])
def process_for_make():
    """Process Google Drive video and return frames as base64 for Make.com"""
    try:
        # Get data from Make.com
        data = request.get_json()
        share_link = data.get('share_link') or data.get('gdrive_link') or data.get('url')
        
        if not share_link:
            return jsonify({
                'success': False,
                'error': 'Share link is required. Send as "share_link", "gdrive_link", or "url"'
            }), 400
        
        # Optional parameters with defaults
        fps_interval = data.get('fps_interval', 5)
        quality = data.get('quality', 2)
        
        # Download and process video
        result, message = download_and_process_video(
            share_link, 
            fps_interval=fps_interval, 
            quality=quality,
            keep_video=False
        )
        
        if not result:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Encode frames to base64
        encoded_frames = encode_frames_to_base64(result['frames'])
        
        # Prepare response for Make.com
        response_data = {
            #'success': True,
            #'message': 'Video processed successfully',
            #'frame_count': len(encoded_frames),
            #'fps_interval': fps_interval,
            #'quality': quality,
            'frames': encoded_frames
        }
        
        # Clean up temporary files
        cleanup_paths = [result['output_dir']]
        if result.get('original_video_path'):
            cleanup_paths.append(result['original_video_path'])
        
        cleanup_temp_files(cleanup_paths)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
