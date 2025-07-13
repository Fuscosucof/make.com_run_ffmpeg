from video_load import download_video_from_gdrive, get_video_stream
from ffmpeg_run_and_encode import process_video_with_ffmpeg
import os
import tempfile 


def download_and_process_video(share_link, output_dir=None, fps_interval=5, quality=2, keep_video=False):
    """Download video from Google Drive and process with FFmpeg"""
    # Download video
    video_path, message = download_video_from_gdrive(share_link)
    
    if not video_path:
        return None, message
    
    try:
        # Process with FFmpeg
        result, process_message = process_video_with_ffmpeg(
            video_path, output_dir, fps_interval, quality
        )
        
        if result:
            result['original_video_path'] = video_path if keep_video else None
            
            # Clean up temporary video file unless keeping it
            if not keep_video:
                try:
                    os.unlink(video_path)
                    #print(f"Deleted temporary video file: {video_path}")
                except:
                    pass
            
            return result, process_message
        else:
            # Clean up video file on failure
            try:
                os.unlink(video_path)
            except:
                pass
            return None, process_message
            
    except Exception as e:
        # Clean up video file on error
        try:
            os.unlink(video_path)
        except:
            pass
        return None, f"Error: {str(e)}"
    
#output_dir = "frames"
#share_link = "https://drive.google.com/file/d/1-BWBE_0s9WiD8N10Eskk1AbfXb1tjqrW/view?usp=drive_link"
#result, message = download_and_process_video(share_link, output_dir=output_dir, fps_interval=5, quality=2, keep_video=False)
#print(result, message)  # Should print the result dictionary and success message or error message