import asyncio
from os import path, listdir
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QTime, pyqtSignal

from lofiplayer2 import MusicPlayer
from MainWindow import Ui_MainWindow

import worker
base_dir = path.normpath(path.expanduser('~/Documents/Study-with-me'))  # base resource directory.


# show help_bubble when hovering over a button
def show_help_bubble(widget, text):
    # Get the global position of the widget
    pos = widget.mapToGlobal(widget.rect().topRight())

    # Display the tooltip at the widget's position
    QtWidgets.QToolTip.showText(pos, text, widget)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    closed = pyqtSignal()  # Custom signal to indicate the window is closed

    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Disable the maximize button
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        # GUI initialization
        self.study_length = None
        self.break_length = None
        self.now = QTime.currentTime()
        self.n_of_session = 0
        self.first_session = QTime.currentTime()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # initial todolist, timer and now_playing
        self.todo_load()
        self.timer_reset()
        # played_lofi_path = path.join(base_dir, 'log', 'played_lofi.txt')
        # f = open(played_lofi_path, 'a+', encoding="utf-8")
        # f.close()

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

        # start nb now_playing button
        # self.nb_music_button.clicked.connect(self.nb_start)

        # todolist default
        self.apply_default_button.clicked.connect(self.default_todo)

        # todolist remove buttons
        self.removeButton_1.clicked.connect(lambda: self.remove_todo(1))
        self.removeButton_2.clicked.connect(lambda: self.remove_todo(2))
        self.removeButton_3.clicked.connect(lambda: self.remove_todo(3))
        self.removeButton_4.clicked.connect(lambda: self.remove_todo(4))
        self.removeButton_5.clicked.connect(lambda: self.remove_todo(5))

        # todolist txt io
        self.load_todo_txt_button.clicked.connect(self.todo_load)
        self.update_todo_button.clicked.connect(self.todo_update)

        # todolist checkbox
        self.todo_1.toggled.connect(self.todo_update)
        self.todo_2.toggled.connect(self.todo_update)
        self.todo_3.toggled.connect(self.todo_update)
        self.todo_4.toggled.connect(self.todo_update)
        self.todo_5.toggled.connect(self.todo_update)

        # todolist current doing radio
        self.todoRadio_1.toggled.connect(lambda: self.change_current_doing(1))
        self.todoRadio_2.toggled.connect(lambda: self.change_current_doing(2))
        self.todoRadio_3.toggled.connect(lambda: self.change_current_doing(3))
        self.todoRadio_4.toggled.connect(lambda: self.change_current_doing(4))
        self.todoRadio_5.toggled.connect(lambda: self.change_current_doing(5))

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

        currently_doing_path = path.join(base_dir, 'log', 'currently_doing.txt')
        with open(currently_doing_path, 'w+', encoding="utf-8") as f:
            f.write(todo_content + spacing)

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

            sr_path = path.join(base_dir, 'log', 'study_rest.txt')  # path for 'study_rest.txt'
            if item[-1] != 'r':
                # if study time, update 'study_rest.txt' as 's' and play lofi
                with open(sr_path, 'w+', encoding="utf-8") as f:
                    f.write('s')
                music_play = asyncio.create_task(self.music_player.player_wrapper(session))

            elif item[-1] == 'r':
                # if rest time, update 'study_rest.txt' as 'r' and play music from nb
                self.music_player.stop_music()
                with open(sr_path, 'w+', encoding="utf-8") as f:
                    f.write('r')

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
