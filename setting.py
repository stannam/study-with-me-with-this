import asyncio
import sys
from os import path, listdir
from PyQt5.QtWidgets import (QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QToolTip,
                             QTimeEdit, QLabel, QPushButton, QMessageBox, QLineEdit, QGridLayout, QSpacerItem,
                             QSizePolicy, QGroupBox, QRadioButton, QCheckBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTime, pyqtSignal

from lofiplayer2 import MusicPlayer
import worker
import state

base_dir = path.normpath(path.expanduser('~/Documents/Study-with-me'))  # base resource directory.


# show help_bubble when hovering over a button
def show_help_bubble(widget, text):
    # Get the global position of the widget
    pos = widget.mapToGlobal(widget.rect().topRight())

    # Display the tooltip at the widget's position
    QToolTip.showText(pos, text, widget)


class MainWindow(QMainWindow):
    closed = pyqtSignal()  # Custom signal to indicate the window is closed

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study session setting")

        # os dependent matters:
        if state.os == 'darwin':
            self.setGeometry(200, 200, 830, 400)
        else:
            self.setGeometry(200, 200, 650, 300)

        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)

        self.initialize_ui()
        self.setCentralWidget(self.main_widget)

        # Disable the maximize button
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        # GUI initialization
        self.study_length = None
        self.break_length = None
        self.now = QTime.currentTime()
        self.n_of_session = 0
        self.first_session = QTime.currentTime()
        icon = QIcon()
        if getattr(sys, 'frozen', False):
            # If frozen (executable), use sys._MEIPASS to get the bundle directory
            icon_path = path.join(sys._MEIPASS,'icons', 'icon.ico')
        else:
            # If running as a script, use the current directory
            icon_path = 'icons/icon.ico'
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        # initial todolist, timer and now_playing
        self.todo_load()
        self.timer_reset()

        # load lofi player
        self.music_player = MusicPlayer()

        # volume control (volume up/down/mute) when clicked
        self.volume_up.clicked.connect(lambda: self.volume_con('up'))
        self.volume_down.clicked.connect(lambda: self.volume_con('down'))
        self.volume_mute.clicked.connect(lambda: self.volume_con('mute'))

        # volume control (show current volume) when hovered over
        self.volume_up.enterEvent = lambda event: show_help_bubble(self.volume_up,
                                                                   f'Volume: {self.music_player.get_volume() * 100:.2f}%')
        self.volume_down.enterEvent = lambda event: show_help_bubble(self.volume_down,
                                                                     f'Volume: {self.music_player.get_volume() * 100:.2f}%')
        self.volume_mute.enterEvent = lambda event: show_help_bubble(self.volume_mute,
                                                                     f'Volume: {self.music_player.get_volume() * 100:.2f}%')

        # default timer button
        self.default_button.clicked.connect(self.timer_reset)

        # to now button
        self.to_now_button.clicked.connect(self.timer_to_now)

        # start timer button
        self.start_button.clicked.connect(self.timer_start)

        # todolist default
        self.apply_default_button.clicked.connect(self.default_todo)

        # todolist txt io
        self.load_todo_txt_button.clicked.connect(self.todo_load)
        self.update_todo_button.clicked.connect(self.todo_update)

        for i in range(1, 6):
            # todolist remove buttons
            getattr(self, f"removeButton_{i}").clicked.connect(lambda checked, idx=i: self.remove_todo(idx))

            # Connect checkboxes
            getattr(self, f"todo_{i}").toggled.connect(self.todo_update)

            # Connect radio buttons
            getattr(self, f"todoRadio_{i}").toggled.connect(
                lambda checked, idx=i: self.change_current_doing(idx)
            )

    def initialize_ui(self):
        btn_height = 30
        left_groupbox = self.left_panel(unit_btn_height=btn_height)    # do the left side for timer and volumes
        right_groupbox = self.right_panel(unit_btn_height=btn_height)  # do the right side for doto list

        self.main_layout.addWidget(left_groupbox, stretch=2)
        self.main_layout.addWidget(right_groupbox, stretch=3)

    def left_panel(self, unit_btn_height):
        lineEdit_width = 40
        left_groupbox = QGroupBox("Timer settings")
        left_layout = QVBoxLayout()

        # timer
        timer_layout = QGridLayout()

        time_label = QLabel("Start studying at:")
        time_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.timerEdit = QTimeEdit()
        self.to_now_button = QPushButton("← To now")

        session_label_1 = QLabel("with")
        session_label_1.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.session_count_lineEdit = QLineEdit()
        self.session_count_lineEdit.setFixedWidth(lineEdit_width)
        session_label_2 = QLabel("sessions of")

        self.study_length_lineEdit = QLineEdit()
        self.study_length_lineEdit.setFixedWidth(lineEdit_width)
        session_label_3 = QLabel("—   ")
        self.break_length_lineEdit = QLineEdit()
        self.break_length_lineEdit.setFixedWidth(lineEdit_width)

        # row 0
        timer_layout.addWidget(time_label, 0, 0, 1, 3)   # spans across 1 row and 2 columns
        timer_layout.addWidget(self.timerEdit, 0, 3)
        timer_layout.addWidget(self.to_now_button, 0, 4)

        # row 1
        timer_layout.addWidget(session_label_1, 1, 0)
        timer_layout.addWidget(self.session_count_lineEdit, 1, 1, 1, 2)
        timer_layout.addWidget(session_label_2, 1, 3)

        # row 2
        timer_layout.addWidget(self.study_length_lineEdit, 2, 0, 1, 2)
        timer_layout.addWidget(session_label_3, 2, 2)
        timer_layout.addWidget(self.break_length_lineEdit, 2, 3)

        # row 3
        timer_layout.addWidget(QLabel("(study time - break time, e.g., 50 - 10)"), 3, 0, 1, 5)

        # Add grid layout to left_layout
        left_layout.addLayout(timer_layout)

        # Add vertical spacer between timer layout and buttons
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # volume control and defult + start buttons
        control_layout = QGridLayout()
        if state.os != 'darwin':
            control_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
            control_layout.setSpacing(0)                   # Remove spacing between widgets

        self.volume_mute = QPushButton("🔇")
        self.volume_mute.setFixedHeight(unit_btn_height * 4)
        self.volume_up = QPushButton("🔊")
        self.volume_up.setFixedHeight(unit_btn_height * 2)
        self.volume_down = QPushButton("🔉")
        self.volume_down.setFixedHeight(unit_btn_height * 2)

        self.default_button = QPushButton("Default")
        self.default_button.setFixedHeight(unit_btn_height)
        self.start_button = QPushButton("START")
        start_btn_font = self.start_button.font()
        start_btn_font.setBold(True)
        start_btn_font.setPointSize((start_btn_font.pointSize() + 2))
        self.start_button.setFont(start_btn_font)
        self.start_button.setFixedHeight(unit_btn_height * 3)

        if state.os != 'darwin':
            for button in [self.volume_mute, self.volume_up, self.volume_down, self.default_button, self.start_button]:
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # column 1 and 2
        control_layout.addWidget(self.volume_mute, 0, 0, 4, 1)
        control_layout.addWidget(self.volume_up, 0, 1, 2, 1)
        control_layout.addWidget(self.volume_down, 2, 1, 2, 1)

        # column 3: Add column spacing
        control_layout.setColumnStretch(2, 1)

        # column 4
        control_layout.addWidget(self.default_button, 0, 3, 1, 1)
        control_layout.addWidget(self.start_button, 1, 3, 3, 1)

        # Add column stretch to distribute available space evenly
        control_layout.setColumnStretch(0, 1)  # Column 1
        control_layout.setColumnStretch(1, 1)  # Column 2
        control_layout.setColumnStretch(3, 1)  # Column 4

        left_layout.addLayout(control_layout)
        left_groupbox.setLayout(left_layout)
        return left_groupbox

    def right_panel(self, unit_btn_height):
        right_groupbox = QGroupBox("Todo list")
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        # To do list
        todo_layout = QGridLayout()
        todo_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
        if state.os == 'darwin':
            todo_layout.setSpacing(6)

        for i in range(1, 6):  # number 1 to 5
            # each line
            remove_btn = QPushButton("Remove")
            rb = QRadioButton()
            cb = QCheckBox()
            todo_text = QLineEdit()

            setattr(self, f'removeButton_{i}', remove_btn)
            setattr(self, f'todo_{i}', cb)
            setattr(self, f'todoRadio_{i}', rb)
            setattr(self, f'todoText_{i}', todo_text)

            # add widgets to the layout
            todo_layout.addWidget(remove_btn, i - 1, 0)  # row=i-1, column=0
            todo_layout.addWidget(rb, i - 1, 1)  # row=i-1, column=1
            todo_layout.addWidget(cb, i - 1, 2)  # row=i-1, column=2
            todo_layout.addWidget(todo_text, i - 1, 3)  # row=i-1, column=3
        right_layout.addLayout(todo_layout)

        # spacer
        right_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # to do-related buttons
        btns_layout = QGridLayout()
        if state.os != 'darwin':
            btns_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
            btns_layout.setSpacing(0)                   # Remove spacing between widgets

        self.apply_default_button = QPushButton("Apply default")
        self.apply_default_button.setFixedHeight(unit_btn_height)
        self.load_todo_txt_button = QPushButton("Load saved\ntodo")
        self.load_todo_txt_button.setFixedHeight(unit_btn_height * 3)
        self.update_todo_button = QPushButton("UPDATE\nTODO")
        self.update_todo_button.setFixedHeight(unit_btn_height * 3)

        btns_layout.addWidget(self.apply_default_button, 0, 1, 1, 2)
        btns_layout.addWidget(self.load_todo_txt_button, 1, 1)
        btns_layout.addWidget(self.update_todo_button, 1, 2)

        # Add column stretch to distribute available space evenly
        for col_n in range(3):
            btns_layout.setColumnStretch(col_n, 1)  # Column 1

        right_layout.addLayout(btns_layout)

        right_groupbox.setLayout(right_layout)
        return right_groupbox

    def change_current_doing(self, i=0):
        if i == 0:
            for j in range(5):
                target_radio = getattr(self, f'todoRadio_{j + 1}')
                if target_radio.isChecked():
                    self.change_current_doing(j + 1)
                    break
            return
        todo_content = getattr(self, f'todoText_{i}')
        todo_content = todo_content.text()
        spacing_length = 18 - len(todo_content)
        spacing = ' ' * spacing_length if spacing_length > 0 else '         '

        state.currently['doing'] = todo_content + spacing

    def default_todo(self):
        target_lineEdit = getattr(self, 'todoText_1')
        target_checkbox = getattr(self, 'todo_1')
        target_checkbox.setChecked(False)
        target_lineEdit.setText('행정업무 TA stuff etc.')

    def timer_reset(self):
        self.timer_to_now()
        self.session_count_lineEdit.setText('5')
        self.study_length_lineEdit.setText('50')
        self.break_length_lineEdit.setText('10')

    def timer_to_now(self):
        self.timerEdit.setTime(QTime.currentTime())

    def todo_load(self):
        todolist_path = path.join(base_dir, 'log', 'todolist.txt')
        if not path.isfile(todolist_path):
            return
        with open(todolist_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            for index, line in enumerate(lines[1:-1]):
                file_todo_state = line[0]
                file_todo_content = line[3:].strip()

                app_todo_state = getattr(self, f'todo_{index + 1}')
                app_todo_content = getattr(self, f'todoText_{index + 1}')

                if file_todo_state == '☑':
                    app_todo_state.setChecked(True)
                else:
                    app_todo_state.setChecked(False)
                app_todo_content.setText(file_todo_content)

    def todo_update(self):
        todo_list = "                TODAY'S TODO LIST\n"
        for int in range(1, 6):
            todo_state = getattr(self, f'todo_{int}')
            todo_text = getattr(self, f'todoText_{int}').text()

            if todo_state.checkState() == 2:
                todo_list += '☑  '
            else:
                todo_list += '□  '

            todo_list += f'{todo_text}\n'
        todo_list += '                                                  '
        todolist_path = path.join(base_dir, 'log', 'todolist.txt')
        with open(todolist_path, 'w+', encoding="utf-8") as f:
            f.write(todo_list)
        self.change_current_doing()  # update 'currently doing' prompt just in case

    def volume_con(self, con):
        if con == 'up':
            self.music_player.volume_up()
        elif con == 'down':
            self.music_player.volume_down()
        else:
            self.music_player.toggle_mute()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Exit", "Are you sure?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No, )

        if reply == QMessageBox.Yes:
            current_task_set = asyncio.all_tasks()
            asyncio.create_task(self.cancel_existing_tasks(current_task_set))
            self.closed.emit()
            event.accept()
        else:
            event.ignore()

    def remove_todo(self, i=1):
        target_lineEdit = getattr(self, f'todoText_{i}')
        target_checkbox = getattr(self, f'todo_{i}')
        target_lineEdit.setText('')
        target_checkbox.setChecked(False)

        for ind in range(i + 1, 7):
            try:
                original_change = getattr(self, f'todoText_{ind}')
                original_cb = getattr(self, f'todo_{ind}')
            except AttributeError:
                current_text = getattr(self, f'todoText_{ind - 1}')
                current_cb = getattr(self, f'todo_{ind - 1}')
                current_text.setText('')
                current_cb.setChecked(False)

                break
            target_change = getattr(self, f'todoText_{ind - 1}')
            target_cb = getattr(self, f'todo_{ind - 1}')

            old_todo_text = original_change.text()
            old_todo_state = original_cb.checkState()
            if target_change.text() == '':
                target_change.setText(old_todo_text)
                target_cb.setChecked(old_todo_state)
                original_change.setText('')
        self.todo_update()

    def timer_start(self):
        # when 'start timer' button is clicked, start the timer
        try:
            current_task_set = asyncio.all_tasks()  # get all previous tasks. For killing existing timers in advance.
        except RuntimeError:
            current_task_set = set()  # fail-safe. when the program runs for the first time and no existing event loop
        if len(current_task_set) > 1:
            for t in current_task_set:
                if t._callbacks is not None:
                    print('need to kill this task')
                    print('kill it')
            asyncio.create_task(self.cancel_existing_tasks(current_task_set))
        lofi_check_res = self.lofi_check()  # make sure mp3 files are in the folder. If not, do not run.
        if lofi_check_res == 1:
            # there was no music file in the music folder. do nothing.
            return

        countdown_list = list()
        self.first_session = self.timerEdit.time()
        self.n_of_session = int(self.session_count_lineEdit.text())
        self.study_length = int(self.study_length_lineEdit.text())
        self.break_length = int(self.break_length_lineEdit.text())
        self.now = QTime.currentTime()

        # update the timetable only
        worker.by_num_of_sessions(t=self.n_of_session,
                                  first_session_time=self.first_session.toPyTime(),
                                  timetable_only=True,
                                  study_length=self.study_length,
                                  break_length=self.break_length)

        # below is for actually running the timer
        time_difference = self.now.secsTo(self.first_session)
        if 0 < time_difference < 60 * max(self.break_length, self.study_length):
            countdown_list.append(f'{self.first_session.toString("hh:mm")}r ')

        for i in range(self.n_of_session):
            study_session_end = self.first_session.addSecs(
                60 * self.study_length * (i + 1) + 60 * self.break_length * i)
            break_session_end = study_session_end.addSecs(60 * self.break_length)
            if self.reasonable_timerange(study_session_end):
                countdown_list.append(f'{study_session_end.toString("hh:mm")} ')
            if self.reasonable_timerange(break_session_end):
                countdown_list.append(f'{break_session_end.toString("hh:mm")}r ')

        task_timer = asyncio.create_task(self.timer_task(countdown_list))

    def reasonable_timerange(self, time):
        minute_max_var = (self.study_length + self.break_length) * self.n_of_session
        minute_diff = self.now.secsTo(time) / 60
        if minute_diff < -(6 * 60):
            return True
        return 0 < minute_diff < minute_max_var

    def lofi_check(self):
        # check music folder and make sure lofi music is there
        # return 0 if okay to go; # return 1 if no music
        lofi_path = path.join(base_dir, 'resource', 'sound', 'lofi')
        music_files = [f for f in listdir(lofi_path) if f.endswith(".mp3")]
        if len(music_files) == 0:
            QMessageBox.critical(self, "No music found",
                                 f"There is no music to play in the following path\n{lofi_path}\n"
                                 f"Please make sure to download lofi music.\n"
                                 f"Consider\nhttps://lofigirl.com/releases/")
            return 1
        return 0

    async def timer_task(self, cd_list):
        for item in cd_list:
            item = item.strip()
            then_h, then_m = item.split(':')
            now = QTime.currentTime()
            try:
                then = QTime(int(then_h), int(then_m), 0)
            except ValueError:
                then = QTime(int(then_h), int(then_m[:-1]), 0)
            session = now.secsTo(then)
            session = session + 86400 if session < 0 else session

            if item[-1] != 'r':
                state.study_or_rest = 's'
                music_play = asyncio.create_task(self.music_player.player_wrapper(session))

            elif item[-1] == 'r':
                self.music_player.stop_music()
                state.study_or_rest = 'r'

            task = asyncio.create_task(worker.a_countdown(item, time_table=True))
            await task

    async def cancel_existing_tasks(self, current_task_set):
        for t in current_task_set:
            if 'MainWindow' not in str(t):
                t.cancel()
            # try:
            #     await t
            # except asyncio.CancelledError:
            #     print('killed it')
        await asyncio.sleep(1)
