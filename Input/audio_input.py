"""
This module will handle taking of inputs for main function
"""
import os

class AudioInput:
    """
    Handle audio file path input and validation
    """
    def __init__(self):
        self.audio_path = None

    def get_path_from_user(self):
        path = input("enter path of audio file: ").strip()

        #input the path without quates but if used the quates then do below
        
        if (path.startswith("'")and path.endswith("'")) or (path.startswith('"') and path.endswith('"')):
            path = path[1:-1]

        #normalize path(windows friendly)
        path = os.path.normpath(path)
        self .audio_path = path

        return self.audio_path

    def validate_audio_path(self):
        if not self.audio_path:
            print("no audio path set")
            return False
        
        elif not os.path.exists(self.audio_path):
            print("audio path non existant")
            return False
        

        else:
            return True
        
class Outputpath:
    """
    Handles output folder path and validation
    """
    def __init__(self):
        self.output_dir = None

    def get_path_from_user(self):
        path = input("enter path of output folder: ").strip()
        if (path.startswith("'")and path.endswith("'")) or (path.startswith('"') and path.endswith('"')):
            path = path[1:-1]

        #normalize path(windows friendly)
        path = os.path.normpath(path)
        self.output_dir = path

        return self.output_dir
    
    def create(self):
        #print("folder doesnot exist making new one")
        
        try:
            os.makedirs(self.output_dir)
            #print("Folder created successfully")
            return True
        except Exception as e:
            #print("failed to create folder")
            return False

        
    def validate(self):
        if not self.output_dir:
            print("no audio path set")
            return False

        
        elif not os.path.exists(self.output_dir):

            self.create()
            return True
        

        else:
            return True
    

'''
if __name__ == "__main__":
    ai = Outputpath()
    ai.get_path_from_user()
    if ai.validate():
        print("valid")
    else:
        print("invalid")
'''