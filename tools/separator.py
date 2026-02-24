# tools/separator.py
import os
import subprocess
import logging
from pathlib import Path

# Configure the standard logger for this module
# Defines the format: [Time] - [Level] - [Message]
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Tool-Separator")

def separate_audio(input_file_path: str, output_dir: str = "workspace/separated") -> dict:
    """
    Executes the Demucs model to separate an audio track into distinct stems (vocals, drums, bass, other).
    
    Args:
        input_file_path (str): The absolute or relative path to the input audio file.
        output_dir (str): The root directory where the separated stems will be saved.
        
    Returns:
        dict: A dictionary containing the absolute paths of the separated stems, 
              or an error message if the process fails.
    """
    logger.info(f"Starting audio separation for: {input_file_path}")
    
    # Ensure the output workspace directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Extract the base filename without extension
    file_name = Path(input_file_path).stem
    
    # Construct the Demucs command using the efficient 'htdemucs' model
    command = [
        "demucs",
        "-n", "htdemucs",
        "-o", output_dir,
        input_file_path
    ]
    
    try:
        # Execute the subprocess synchronously
        logger.info("Running Demucs model... This may take a while depending on the audio length.")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Demucs default output structure: output_dir/htdemucs/file_name/
        target_folder = Path(output_dir) / "htdemucs" / file_name
        
        # Verify the generated stems
        tracks = ["vocals.wav", "drums.wav", "bass.wav", "other.wav"]
        output_paths = {}
        
        for track in tracks:
            track_path = target_folder / track
            if track_path.exists():
                output_paths[track.split('.')[0]] = str(track_path.absolute())
            else:
                error_msg = f"Expected output file not found: {track_path}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        logger.info(f"Separation completed successfully! Stems saved at: {target_folder}")
        return {"status": "success", "tracks": output_paths}
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Demucs execution failed. Subprocess error: {e.stderr}"
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

# ==========================================
# Local testing block
# ==========================================
if __name__ == "__main__":
    # Specify a valid audio file path for local testing
    test_audio = "test.mp3" 
    
    if os.path.exists(test_audio):
        logger.info("Initiating local test run...")
        results = separate_audio(test_audio)
        logger.info(f"Final JSON payload to return to LLM Agent: {results}")
    else:
        logger.warning(f"Test file '{test_audio}' not found. Please place an audio file in the current directory.")