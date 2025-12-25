"""
This file is used to validate the input audio file
to cheack
        ->filetype
        ->sample rate
        ->corruption
"""
import os
import soundfile as sf

class AudioInfo:
    """
    Reads and store basic information about audio file.
    """
    SUPPORTED_EXTENSIONS = (".wav",".flac",".mp3")

    def __init__(self,audio_path: str):
        
        #dtore normalized path
        self.audio_path = os.path.normpath(audio_path)

        #placeholders for audio properties
        self.sample_rate = None
        self.Channels = None
        self.duration = None
        self.subtype = None

    def is_supported_formate(self)->bool:
        """
        cheack if file extension is one of hte supported formates.
        """

        _,ext = os.path.splitext(self.audio_path)
        ext = ext.lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    def analyze(self)->bool:
        """
        open the audio file read meta data and store it in object
        returns true on success and false on error 
        """

        if not os.path.exists(self.audio_path):
            print("Audio file doesnt exist on disk")
            return False
        elif not self.is_supported_formate():
            print(f"[Audio_info] unsupported file formate for: {self.audio_path}")
            print(f"[AudioInfo] Supported formates: {self.SUPPORTED_EXTENSIONS}")
            return False
        

        try:
            with sf.SoundFile(self.audio_path)as f:
                self.sample_rate = f.samplerate
                self.channels = f.channels
                self.subtype = f.subtype
                #duration = total_frames/sample_rate
                self.duration = len(f)/float(f.samplerate)

            return True
        except Exception as e:
            print(f"[Audio_info] Failed to read audio file: {e}")
            return False
        
    def pretty_print(self):
        """
        Print audio information in a human-readable way
        """
        if self.sample_rate is None:
            print("[AudioInfo] No info available. Did you call analyze()?")
            return

        print("=== Audio File Info ===")
        print(f"Path       : {self.audio_path}")
        print(f"Format     : {self.subtype}")
        print(f"SampleRate : {self.sample_rate} Hz")
        print(f"Channels   : {self.channels}")
        print(f"Duration   : {self.duration:.2f} seconds")
        print("=======================")


if __name__ == "__main__":
    from audio_input import AudioInput

    ai = AudioInput()
    path = ai.get_path_from_user()

    if not ai.validate_audio_path():
        print("❌ Invalid audio path. Exiting.")
    else:
        info = AudioInfo(path)
        if info.analyze():
            info.pretty_print()
        else:
            print("❌ Could not analyze audio file.")


