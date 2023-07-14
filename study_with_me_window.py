import sys
from os import getcwd, path, name
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtMultimedia import QCamera, QCameraInfo

RESOURCE_PATH = path.join(getcwd(), 'log')


def read_resource(filename):
    extension = filename.split('.')[-1]
    file_path = path.join(RESOURCE_PATH, filename)
    if extension == 'html':
        return QUrl.fromLocalFile(file_path)
    elif extension == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Study with me")
        system = sys.platform
        if system.startswith('win'):
            self.os = 'win'
            self.setFixedSize(1600, 900)  # Set fixed window size
            self.setWindowFlag(Qt.WindowStaysOnTopHint)  # Make window always on top
            self.heights = [ # total = 900px
                            150,  # local time clock
                            220,  # timetable
                            50,  # study_time / break_time
                            80,  # count down
                            400]  # to-do list
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
        elif system.startswith('darwin'):
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

        self.camera = None  # Define the camera attribute
        self.viewfinder = None  # Define the viewfinder attribute

        # Create the main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Create the left panel with camera and floating text ticker
        left_panel = QWidget(self)
        left_layout = QVBoxLayout(left_panel)
        left_panel.setStyleSheet("background-color: rgb(0, 0, 0);")  # Set the background color to black

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
        #self.viewfinder.setFixedWidth(50)  # Set the fixed width of the viewfinder
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

        left_layout.addWidget(camera_label, 9)  # Allocate 90% of vertical space
        left_layout.addWidget(ticker_label, 1)  # Allocate 10% of vertical space

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


        # Right sub-part for showing either 'study time' or 'break time'
        self.study_break_label = QLabel('STUDY TIME')
        self.study_break_label.setStyleSheet(self.styles["study_break_label"])
        self.study_break_label.setAlignment(Qt.AlignCenter)
        self.study_break_label.setMinimumHeight(heights[2])
        self.study_break_label.setMaximumHeight(heights[2])
        right_layout.addWidget(self.study_break_label)

        # Right sub-part with content from "[STUDY]_DOWN.txt" file
        self.study_down_label = QLabel(read_resource('[STUDY]_DOWN.txt'))
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
            right_layout.addWidget(ticker_label,1)
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
        self.currently_doing_text.setText(read_resource('currently_doing.txt')[:self.letter_limit])
        self.current_music_text.setText(read_resource('current_lofi.txt')[:self.letter_limit])
        self.todolist_label.setText(read_resource('todolist.txt'))
        self.update_study_rest()

    def update_study_rest(self):
        with open(path.join(getcwd(),'log','study_rest.txt'), 'r', encoding='utf-8') as f:
            study_or_rest = f.read()

        if 'r' in study_or_rest:
            countdown_file = '[BREAK]_TIME.txt'
            study_break = 'BREAK TIME'
            self.study_down_label.setStyleSheet(self.styles["rest_down_label"])

        else:
            countdown_file = '[STUDY]_DOWN.txt'
            study_break = 'STUDY TIME'
            self.study_down_label.setStyleSheet(self.styles["study_down_label"])
        self.study_down_label.setText(read_resource(countdown_file))
        self.study_break_label.setText(study_break)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

