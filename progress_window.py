import sys
from os import path
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, \
    QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtMultimedia import QCamera, QCameraInfo

import state

RESOURCE_PATH = path.join(path.normpath(path.expanduser('~/Documents/Study-with-me')), 'log')


def read_resource(filename):
    extension = filename.split('.')[-1]
    file_path = path.join(RESOURCE_PATH, filename)
    if extension == 'html':
        return QUrl.fromLocalFile(file_path)
    elif extension == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class OngoingWindow(QMainWindow):
    def __init__(self, camera=False):
        super().__init__()

        # flag for ignoring close
        self.ignore_close = True

        # initial gui settings
        self.setWindowTitle("Study with me")
        icon = QtGui.QIcon()
        if getattr(sys, 'frozen', False):
            # If frozen (executable), use sys._MEIPASS to get the bundle directory
            icon_path = path.join(sys._MEIPASS,'icons', 'icon.ico')
        else:
            # If running as a script, use the current directory
            icon_path = 'icons/icon.ico'
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)  # Disable always on top
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)  # Disable close button
        self.setWindowFlag(Qt.WindowTitleHint, False)
        system = sys.platform

        # camera settings
        self.need_camera = camera
        if state.os == 'win32':
            self.os = 'win'
            self.setFixedSize(1600, 900)  # Set fixed window size
            self.heights = [        # total = 900px
                            130,    # local time clock
                            260,    # timetable
                            50,     # study_time / break_time
                            80,     # count down
                            380]    # to-do list
            self.letter_limit = 112
            self.styles = {
                "currently_doing_label": "color: white; font-weight: bold; font-size: 24px;",
                "currently_doing_text": "color: white; font-size: 20px;",
                "current_music_label": "color: white; font-weight: bold; font-size: 24px;",
                "current_music_text": "color: white; font-size: 18px;",
                "study_break_label": "color: white; font-weight: bold; font-family: NanumBarunPen; font-size: 30px;",
                "study_down_label": "color: white; font-weight: bold; font-family: NanumBarunPen; font-size: 90px;",
                "rest_down_label": "color: yellow; font-weight: bold; font-family: NanumBarunPen; font-size: 90px;",
                "todolist_label": "color: white; font-family: NanumBarunPen; font-size: 30px;",
            }

        else:
            self.os = 'mac'
            self.setFixedSize(300, 700)  # Set fixed window size
            self.styles = {
                "currently_doing_label": "color: white; font-weight: bold; font-size: 14px;",
                "currently_doing_text": "color: white; font-size: 12px;",
                "current_music_label": "color: white; font-weight: bold; font-size: 14px;",
                "current_music_text": "color: white; font-size: 12px;",
                "study_break_label": "color: white; font-weight: bold; font-family: NanumBarunPenOTF; font-size: 20px;",
                "study_down_label": "color: white; font-weight: bold; font-family: NanumBarunPenOTF; font-size: 60px;",
                "rest_down_label": "color: yellow; font-weight: bold; font-family: NanumBarunPenOTF; font-size: 60px;",
                "todolist_label": "color: white; font-family: NanumBarunPenOTF; font-size: 14px;",

            }
            self.heights = [  # total = 630px out of 700px
                            90,  # local time clock
                            300,  # timetable
                            40,  # study_time / break_time
                            60,  # count down
                            140]  # to-do list
            self.letter_limit = 80

        # Create the main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Create the left panel with camera and floating text ticker
        left_panel = QWidget(self)
        left_layout = QVBoxLayout(left_panel)
        left_panel.setStyleSheet("background-color: rgb(0, 0, 0);")  # Set the background color to black

        if self.need_camera:
            self.camera = None  # Define the camera attribute
            self.viewfinder = None  # Define the viewfinder attribute

            camera_label = QWidget(self)
            self.camera_layout = QVBoxLayout(camera_label)

            # Initialize the camera selection combo box
            camera_combo = QComboBox(self)  # Move camera_combo to be part of the main window
            camera_combo.currentIndexChanged.connect(self.on_camera_selected)
            self.populate_camera_combo(camera_combo)

            # Initialize and access the selected camera
            self.camera = QCamera(camera_combo.currentData())
            self.camera.setCaptureMode(QCamera.CaptureViewfinder)
            self.viewfinder = QCameraViewfinder()
            self.camera.setViewfinder(self.viewfinder)
            self.camera.start()
            self.camera_layout.addWidget(self.viewfinder)  # Remove the stretch factor parameter
            self.camera_layout.addWidget(camera_combo)  # Add camera_combo to the camera_layout

        ticker_label = QWidget(self)
        ticker_layout = QVBoxLayout(ticker_label)

        # Create ticker1 with two sub-parts
        ticker1_layout = QHBoxLayout()
        ticker1_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0

        # Left sub-part with fixed text "currently doing:"
        currently_doing_label = QLabel("Currently Doing:")
        currently_doing_label.setStyleSheet(self.styles['currently_doing_label'])
        ticker1_layout.addWidget(currently_doing_label, 2)  # Allocate 20% width

        # Right sub-part with content
        self.currently_doing_text = QLabel()
        self.currently_doing_text.setStyleSheet(self.styles["currently_doing_text"])
        ticker1_layout.addWidget(self.currently_doing_text, 8)  # Allocate 80% width

        # add ticker1 (currently doing) to ticker_layout
        ticker_layout.addLayout(ticker1_layout)

        # now let's work on ticker2 (current music)
        ticker2_layout = QHBoxLayout()
        ticker2_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0

        # Left sub-part with fixed text "current music:"
        current_music_label = QLabel("Current music:")
        current_music_label.setStyleSheet(self.styles["current_music_label"])
        ticker2_layout.addWidget(current_music_label, 2)  # Allocate 20% width

        # Right sub-part with actual music title
        self.current_music_text = QLabel()
        self.current_music_text.setStyleSheet(self.styles["current_music_text"])
        ticker2_layout.addWidget(self.current_music_text, 8)  # Allocate 80% width

        # add ticker2 (current music) to ticker_layout
        ticker_layout.addLayout(ticker2_layout)

        if self.need_camera:
            left_layout.addWidget(camera_label, 9)  # Allocate 90% of vertical space
            left_layout.addWidget(ticker_label, 1)  # Allocate 10% of vertical space
        else:
            self.camera_placeholder = QWidget(self)
            self.camera_placeholder.setStyleSheet("background-color: black;")  # Set black background
            left_layout.addWidget(self.camera_placeholder, 9)
            left_layout.addWidget(ticker_label)

        if self.os == "win":
            main_layout.addWidget(left_panel, 7)  # Allocate 70% width

        # Create the right panel with four parts
        right_panel = QWidget(self)
        right_layout = QVBoxLayout(right_panel)
        right_panel.setStyleSheet("background-color: rgb(27, 27, 27);")  # Set the background color to (27, 27, 27)

        # Set the heights of the sub-panels
        heights = self.heights

        # Right sub-part with content from "clock.html" file
        clock_view = QWebEngineView()
        clock_view.load(read_resource('clock.html'))
        clock_view.setMinimumHeight(heights[0])
        clock_view.setMaximumHeight(heights[0])
        right_layout.addWidget(clock_view)

        # Right sub-part with content from "timetable.html" file
        timetable_view = QWebEngineView()
        timetable_view.load(read_resource('timetable.html'))
        timetable_view.setMinimumHeight(heights[1])
        timetable_view.setMaximumHeight(heights[1])
        right_layout.addWidget(timetable_view)

        # Button to refresh "timetable.html" file
        tt_refresh_button = QPushButton("Refresh timetable")
        tt_refresh_button.clicked.connect(lambda: timetable_view.load(read_resource('timetable.html')))
        tt_refresh_button.setMinimumHeight(20)
        tt_refresh_button.setStyleSheet("background-color: rgb(50, 50, 50); color: white;")
        right_layout.addWidget(tt_refresh_button)

        # Right sub-part for showing either 'study time' or 'break time'
        self.study_break_label = QLabel('STUDY TIME')
        self.study_break_label.setStyleSheet(self.styles["study_break_label"])
        self.study_break_label.setAlignment(Qt.AlignCenter)
        self.study_break_label.setMinimumHeight(heights[2])
        self.study_break_label.setMaximumHeight(heights[2])
        right_layout.addWidget(self.study_break_label)

        # Right sub-part with content from timer(in state.timers)
        self.study_down_label = QLabel(state.timers['study'])
        self.study_down_label.setStyleSheet(self.styles["study_down_label"])
        self.study_down_label.setAlignment(Qt.AlignCenter)
        self.study_down_label.setMinimumHeight(heights[3])
        self.study_down_label.setMaximumHeight(heights[3])
        right_layout.addWidget(self.study_down_label)

        # Right sub-part with content from "todolist.txt" file
        self.todolist_label = QLabel(read_resource('todolist.txt'))
        self.todolist_label.setStyleSheet(self.styles["todolist_label"])
        self.todolist_label.setMinimumHeight(heights[4])
        self.todolist_label.setMaximumHeight(heights[4])
        right_layout.addWidget(self.todolist_label)
        if self.os == "mac":
            right_layout.addWidget(ticker_label, 1)
            main_layout.addWidget(right_panel, 4)  # Allocate 40% width
        else:
            main_layout.addWidget(right_panel, 3)  # Allocate 30% width

        # Create a QTimer to update the labels every 500 milliseconds (half a second)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(474)

    def populate_camera_combo(self, combo):
        available_cameras = QCameraInfo.availableCameras()
        for camera in available_cameras:
            combo.addItem(camera.description(), camera)

    def on_camera_selected(self, index):
        selected_camera = self.sender().currentData()
        if self.camera:
            self.camera.stop()
        self.camera = QCamera(selected_camera)
        self.camera.setCaptureMode(QCamera.CaptureViewfinder)
        self.viewfinder = QCameraViewfinder()
        self.viewfinder.setFixedWidth(1120)  # Set the fixed width of the viewfinder
        self.camera.setViewfinder(self.viewfinder)
        self.camera.start()
        self.camera_layout.addWidget(self.viewfinder)

    def update_labels(self):
        # Update the contents of the labels
        self.currently_doing_text.setText(state.currently['doing'][:self.letter_limit])
        self.current_music_text.setText(state.currently['lofi'][:self.letter_limit])
        self.todolist_label.setText(read_resource('todolist.txt'))
        self.update_study_rest()

    def update_study_rest(self):
        study_or_rest = state.study_or_rest
        if 'r' in study_or_rest:
            timer_str = state.timers['break']
            study_break = 'BREAK TIME'
            self.study_down_label.setStyleSheet(self.styles["rest_down_label"])

        else:
            timer_str = state.timers['study']
            study_break = 'STUDY TIME'
            self.study_down_label.setStyleSheet(self.styles["study_down_label"])
        self.study_down_label.setText(timer_str)
        self.study_break_label.setText(study_break)

    def closeEvent(self, event):
        print(f'ignore_close value in ongoing windows: {self.ignore_close}')
        if self.ignore_close:
            msg = QMessageBox.warning(self,
                                      "Close disabled",
                                      "To quit, close the 'settings' window instead.",
                                      QMessageBox.Ok
                                      )
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OngoingWindow()
    window.show()
    sys.exit(app.exec_())
