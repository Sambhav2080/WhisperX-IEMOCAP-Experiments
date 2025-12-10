"""
This file includes the main working of python's WhisperX Module
"""

import json,os
import os
import sys
import torch
import whisperx
from whisperx.diarize import DiarizationPipeline


# ----------------------Add project root to sys.path -----------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# --------------------------------------------------------------------------

# ------------ PyTorch 2.6 workaround: force weights_only=False ------------
_real_torch_load = torch.load

def torch_load_force_weights_false(*args, **kwargs):
    """
    Wrapper around torch.load that forces weights_only=False.
    This bypasses the new PyTorch 2.6 safety default.
    USE ONLY IF YOU TRUST THE CHECKPOINT SOURCE.
    """
    # Agar caller ne khud weights_only diya hai:
    if "weights_only" in kwargs:
        kwargs["weights_only"] = False
    else:
        # Nahi diya to hum khud set kar denge
        kwargs["weights_only"] = False
    return _real_torch_load(*args, **kwargs)

torch.load = torch_load_force_weights_false
# -------------------------------------------------------------------------

class WhisperXRunner:
    """
    Runs whisperX transcription +diarization on Audio files
    """

    def __init__(self,model_name = "medium", device = "cuda"):
        self.model_name = model_name
        self.device = device if torch.cuda.is_available()else "cpu"
        self.model = None
        self.alignment_model = None
        self.diarize_model = None
        self.result = None

    def load_models(self):
        """"D:\Datasets\Datasets\IOMOCAP\IEMOCAP_full_release\IEMOCAP_full_release\Session1\dialog\wav\Ses01F_impro01.wav"
        Load the Whisperx Model and Diarization Model
        """
        print(f"[WhisperX] Loading model {self.model_name} on {self.device}")
        self.model = whisperx.load_model(self.model_name, self.device, compute_type="int8")

        self.alignment_model, self.alignment_metadata = whisperx.load_align_model(language_code="en",device=self.device)

        print("[WhisperX] Loading diarization model...")
        self.diarize_model = DiarizationPipeline(use_auth_token=None, device=self.device)

    def run(self, audio_path: str):
        """
        Execute ASR + Alignment + Diarization
        """
        if self.model is None:
            print("[ERROR] Model not loaded. Call load_models() first.")
            return None
        
        #load audio
        audio = whisperx.load_audio(audio_path)

        print(f"[WhisperX] Transcribing: {audio_path}")
        result = self.model.transcribe(audio_path)

        print("[WhisperX] Running alignment...")
        aligned = whisperx.align(result["segments"],
            self.alignment_model,
            self.alignment_metadata,
            audio,
            self.device)
        
        result["segments"] = aligned["segments"]


        print("[WhisperX] Running diarization...")
        diarize_segments = self.diarize_model(audio_path)

        print("[WhisperX] Assigning diarization to text...")
        result = whisperx.assign_word_speakers(diarize_segments, result)

        self.result = result
        print("[WhisperX] Processing Completed!")
        return result
    
    def save_result(self,output_folder:str,base_name = "result"):
        if self.result is None:
            print("[ERROR] No results to save. Run run() first")
            return False
        save_path = os.path.join(output_folder,f"{base_name}.json")
        with open(save_path,"w",encoding = "utf-8") as f:
            json.dump(self.result,f,ensure_ascii= False,indent = 2)

        print(f"[WhisperX] Result saved at: {save_path}")
        return True
    

'''
if __name__ == "__main__":
    from Input.audio_input import AudioInput,Outputpath

    ai = AudioInput()
    path = ai.get_path_from_user()
    if not ai.validate_audio_path():
        print("invalid path. Exiting")
        exit()

    op = Outputpath()
    out = op.get_path_from_user()
    if not op.validate():
        print("invalid output path. Exiting")
        exit()

    runner = WhisperXRunner()
    runner.load_models()
    result = runner.run(path)
    runner.save_result(out,"whisperx_output")
'''