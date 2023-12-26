# This file checks on User's documents folder to see whether all required files exist
# It should be imported before any other program files.

import sys
from os import path
from shutil import rmtree, copytree
from requests import get
from zipfile import ZipFile
from io import BytesIO

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox, QPushButton

base_dir = path.normpath(path.expanduser('~/Documents/Study-with-me'))  # base resource directory.

if getattr(sys, 'frozen', False):
    # If frozen (executable), use sys._MEIPASS to get the bundle directory
    root_dir = sys._MEIPASS
else:
    # If running as a script, use the current directory
    root_dir = path.abspath(path.dirname(__file__))


# make sure all required data files exist
def resource_check():
    flag = False
    if not path.exists(base_dir):
        # base directory does not exist
        flag = True
    else:
        # base directory exists. now check for required files
        # first, 'log'
        log_dir = path.join(base_dir, 'log')
        required_log_files = ["clock.html",
                              "currently_doing.txt",
                              "current_lofi.txt",
                              "played_lofi.txt",
                              "refresh.js",
                              "study_rest.txt",
                              "tb_metadata.txt",
                              "timetable.html",
                              "timetable.txt",
                              "todolist.txt",
                              "[STUDY]_DOWN.txt",
                              "[BREAK]_TIME.txt"]

        # second, resource folder
        resource_dir = path.join(base_dir, 'resource')
        required_resource_files = ["sound_dir"]

        # third, sound folder
        sound_dir = path.join(base_dir, 'resource', 'sound')
        required_sound_files = ["lofi_dir", "bell1.mp3"]

        dirs = [log_dir, resource_dir, sound_dir]
        files = [required_log_files, required_resource_files, required_sound_files]

        for d, filelist in zip(dirs, files):
            # loop over each required file to check
            for file in filelist:
                if '_dir' in file:
                    to_check = path.join(d, file.split('_')[0])
                else:
                    to_check = path.join(d, file)
                if not path.exists(to_check):
                    flag = True
                    break

    if flag:
        init_res = initialize()
        if init_res == 0:
            return 1  # initialized. need to alert to add lofi musics

    return 0  # all good. launch the program.


def initialize():
    # copy the default data from the source to the user's document folder
    print("[INFO] Now the program will try to initialize local resources.")
    source_log_dir = path.join(root_dir, 'log')
    source_resource_dir = path.join(root_dir, 'resource')

    # first the log folder
    try:
        rmtree(path.join(base_dir, 'log'))
        print("[INFO] Existing 'log' folder deleted.")
    except OSError as e:
        print(f"[ERROR] Error deleting folder: {e}")

    try:
        copytree(source_log_dir, path.join(base_dir, 'log'))
        print("[INFO] 'log' folder copied successfully.")
    except OSError as e:
        print(f"[ERROR] Error copying folder: {e}")

    # now the resource folder
    try:
        rmtree(path.join(base_dir, 'resource'))
        print("[INFO] Existing 'resource' folder deleted.")
    except OSError as e:
        print(f"[ERROR] Error deleting folder: {e}")

    try:
        copytree(source_resource_dir, path.join(base_dir, 'resource'))
        print("[INFO] 'resource' folder copied successfully.")
    except OSError as e:
        print(f"[ERROR] Error copying folder: {e}")

    # populate the music directory so that the program can run out of the box.
    music_dir = path.join(base_dir, 'resource', 'sound', 'lofi')
    r = get('https://github.com/stannam/study-with-me-with-this/raw/master/music_samples/public%20domain.zip')
    # Check if the request was successful (status code 200)
    while True:
        if r.status_code == 200:
            # Open the ZIP file from the response content
            with ZipFile(BytesIO(r.content)) as zip_ref:
                # Extract all contents to the destination folder
                zip_ref.extractall(music_dir)
            print("[INFO] Download and extraction successful.")
            break
        else:
            print(f"[ERROR] Failed to download the file. Status code: {r.status_code}")


    return 0


class WarningDialog(QMessageBox):
    def __init__(self):
        super(WarningDialog, self).__init__()

        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle("Warning")
        self.setText("The local resource files have been initialized.\n"
                     "Please make sure to download Lofi musics.\n"
                     "Open the directory for details")
        open_path_button = QPushButton("Open Path")
        open_path_button.clicked.connect(self.open_music_path)
        self.addButton(open_path_button, QMessageBox.ActionRole)

        self.setStandardButtons(QMessageBox.Ok)

    def open_music_path(self):
        # Open the specified path in the default file manager
        to_path = path.join(base_dir, 'resource', 'sound', 'lofi')
        QDesktopServices.openUrl(QUrl.fromLocalFile(to_path))

