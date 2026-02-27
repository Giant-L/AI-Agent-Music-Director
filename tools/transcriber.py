import os
import logging
import warnings
from pathlib import Path

# 🌟 Silence irrelevant warnings to keep the console clean
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

# Configure the standard logger for the Transcriber Tool
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Tool-Transcriber")

def audio_to_midi(input_file_path: str, output_dir: str = "workspace/midi_outputs") -> dict:
    """
    Converts audio into a MIDI file. 
    Added auto-overwrite logic to prevent 'File exists' errors.
    """
    logger.info(f"Starting Audio-to-MIDI transcription for: {input_file_path}")
    
    # 1. Validate if the input file exists
    if not os.path.exists(input_file_path):
        error_msg = f"Input file not found: {input_file_path}"
        logger.error(error_msg)
        return {"error": error_msg}

    # 2. Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Construct the target MIDI path
    file_name = Path(input_file_path).stem
    expected_midi_path = Path(output_dir) / f"{file_name}_basic_pitch.mid"

    # 🌟 NEW: Overwrite logic to prevent "File already exists" error
    if expected_midi_path.exists():
        logger.info(f"Existing MIDI found at {expected_midi_path}. Deleting for a fresh start...")
        try:
            expected_midi_path.unlink() # Delete the existing file
        except Exception as e:
            logger.warning(f"Could not delete existing MIDI: {e}")

    try:
        logger.info("Running Spotify's Basic-Pitch model...")
        
        # 3. Call the core prediction API
        predict_and_save(
            audio_path_list=[input_file_path],
            output_directory=output_dir,
            save_midi=True,
            sonify_midi=False,
            save_model_outputs=False,
            save_notes=False,
            model_or_model_path=ICASSP_2022_MODEL_PATH 
        )
        
        # 4. Final verification
        if expected_midi_path.exists():
            logger.info(f"Transcription successful! MIDI saved at: {expected_midi_path}")
            return {
                "status": "success", 
                "midi_path": str(expected_midi_path.absolute())
            }
        else:
            error_msg = f"Expected MIDI file was not generated at: {expected_midi_path}"
            logger.error(error_msg)
            return {"error": error_msg}

    except Exception as e:
        error_msg = f"An unexpected error occurred during transcription: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

# ==========================================
# Local testing block
# ==========================================
if __name__ == "__main__":
    test_separated_audio = "workspace/separated/htdemucs/test/other.wav" 
    
    if os.path.exists(test_separated_audio):
        logger.info("Initiating local test run for Transcriber...")
        results = audio_to_midi(test_separated_audio)
        logger.info(f"Final JSON payload to return to LLM Agent: {results}")
    else:
        logger.warning(f"Test file '{test_separated_audio}' not found.")