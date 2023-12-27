# This file checks on User's documents folder to see whether all required files exist
# It should be imported before any other program files.

import sys
from os import path
from shutil import rmtree, copytree
from time import sleep

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton, QWidget, QProgressBar, QVBoxLayout, QLabel, QListWidget, \
    QListWidgetItem

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
    ex = InitialLoader()
    ex.show()
    ex.close()
    return 0


class InitialLoader(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('My Application')
        self.setGeometry(300, 300, 400, 200)

        self.loading_window = LoadingWindow()
        self.loading_window.show()
        self.loading_window.add_message("[INFO] WELCOME. It seems you launched it for the first time.\n"
                                        "Please allow the program to finish initial setup.")
        self.loading_window.set_progress(10)
        QApplication.processEvents()
        sleep(5)

        self.loading_window.add_message("[INFO] Now the program will try to initialize local resources.")
        self.loading_window.set_progress(15)
        QApplication.processEvents()
        source_log_dir = path.join(root_dir, 'log')
        source_resource_dir = path.join(root_dir, 'resource')

        # first the log folder
        try:
            rmtree(path.join(base_dir, 'log'))
            self.loading_window.add_message("[INFO] Existing 'log' folder deleted.")
            QApplication.processEvents()
        except OSError as e:
            self.loading_window.add_message(f"[ERROR] Error deleting folder: {e}")
            QApplication.processEvents()
        self.loading_window.set_progress(30)
        QApplication.processEvents()

        try:
            copytree(source_log_dir, path.join(base_dir, 'log'))
            self.loading_window.add_message("[INFO] 'log' folder copied successfully.")
            QApplication.processEvents()
        except OSError as e:
            self.loading_window.add_message(f"[ERROR] Error copying folder: {e}")
            QApplication.processEvents()
        self.loading_window.set_progress(60)
        QApplication.processEvents()

        # now the resource folder
        try:
            rmtree(path.join(base_dir, 'resource'))
            self.loading_window.add_message("[INFO] Existing 'resource' folder deleted.")
            QApplication.processEvents()
        except OSError as e:
            self.loading_window.add_message(f"[ERROR] Error deleting folder: {e}")
            QApplication.processEvents()
        self.loading_window.set_progress(90)
        QApplication.processEvents()

        try:
            copytree(source_resource_dir, path.join(base_dir, 'resource'))
            self.loading_window.add_message("[INFO] 'resource' folder copied successfully.")
            QApplication.processEvents()
        except OSError as e:
            self.loading_window.add_message(f"[ERROR] Error copying folder: {e}")
            QApplication.processEvents()
        self.loading_window.set_progress(100)
        QApplication.processEvents()

        self.loading_window.close()
        self.close()


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

class LoadingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Loading...')
        self.setGeometry(300, 300, 600, 200)
        self.messages_list = QListWidget()
        self.progress_bar = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(self.messages_list)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def add_message(self, message):
        item = QListWidgetItem(message)
        self.messages_list.addItem(item)
        self.messages_list.scrollToBottom()

    def set_progress(self, value):
        self.progress_bar.setValue(value)

