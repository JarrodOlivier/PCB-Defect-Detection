# https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
import os
import glob
import shutil

def cleanup():
    try:
        shutil.rmtree("Template/") 
        shutil.rmtree("Under_Test/")
    except Exception as e:
        print(e) 
        
    # Directories with the following names are made (useful for first run)
    os.makedirs(os.getcwd()+"/Template/", exist_ok=True)
    os.makedirs(os.getcwd()+"/Under_Test/", exist_ok=True)
    os.makedirs(os.getcwd()+"/Template/Backlight/", exist_ok=True)
    os.makedirs(os.getcwd()+"/Under_Test/Backlight/", exist_ok=True)
     

if __name__ == "__main__":
    cleanup()