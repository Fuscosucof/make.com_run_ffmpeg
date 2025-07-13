import os
import tempfile
import subprocess
import base64
import shutil


def encode_frames_to_base64(frame_paths):
    """Convert frame images to base64 for API response"""
    encoded_frames = []
    
    for i, frame_path in enumerate(frame_paths):
        try:
            with open(frame_path, 'rb') as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                encoded_frames.append({
                    'frame_number': i + 1,
                    'filename': os.path.basename(frame_path),
                    'data': img_base64,
                    'mime_type': 'image/jpeg'
                })
        except Exception as e:
            print(f"Error encoding frame {frame_path}: {e}")
            continue
    
    return encoded_frames

def process_video_with_ffmpeg(video_path, output_dir=None, fps_interval=5, quality=2):
    """Process video with FFmpeg to extract frames"""
    if not os.path.exists(video_path):
        return None, "Video file not found"
    
    # Create output directory if not provided
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Output pattern for frames
    output_pattern = os.path.join(output_dir, "frame_%03d.jpg")
    
    try:
        # FFmpeg command to extract frames
        command = [
            "ffmpeg", "-i", video_path,
            "-vf", f"fps=1/{fps_interval}",
            "-q:v", str(quality),
            "-y",  # Overwrite output files
            output_pattern
        ]
        
        # Run FFmpeg
        result = subprocess.run(command, 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            # Get list of created frames
            frames = [f for f in os.listdir(output_dir) if f.endswith('.jpg')]
            frames.sort()
            frame_paths = [os.path.join(output_dir, f) for f in frames]
            encoded_frames = encode_frames_to_base64(frame_paths)
            
            return {
                'success': True,
                'output_dir': output_dir,
                'frames': frame_paths,
                'encoded_frames': encoded_frames,
                'frame_count': len(frames),
                'ffmpeg_output': result.stdout
            }, "Success"
        else:
            return None, f"FFmpeg error: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return None, "FFmpeg processing timed out"
    except FileNotFoundError:
        return None, "FFmpeg not found. Please install FFmpeg"
    except Exception as e:
        return None, f"Error processing video: {str(e)}"
    
#output_dir = "frames"
#video_path = "D:\\VS\\ML, LLMs, AI\\ffmpeg_http\\uploads\\COWS_AT_THE_GRASS (1).mp4"
#result = process_video_with_ffmpeg(video_path, output_dir=output_dir, fps_interval=5, quality=2)
#print(result)  # Should print the result dictionary and success message or error message