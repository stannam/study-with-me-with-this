import subprocess
import sys
import os
import asyncio
import qasync
from PyQt5.QtWidgets import QAction

import lofiplayer
import main
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTime


from MainWindow import Ui_MainWindow

# use 'pyuic5 resource/mainwindow.ui -o MainWindow.py' on terminal

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # initial todolist, timer and now_playing
        self.todo_load()
        self.timer_reset()
        self.nb_start()

        # default timer button
        self.default_button.clicked.connect(self.timer_reset)

        # to now button
        self.to_now_button.clicked.connect(self.timer_to_now)

        # start timer button
        self.start_button.clicked.connect(self.timer_start)

        # start nb now_playing button
        self.nb_music_button.clicked.connect(self.nb_start)

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

        # todolist current doing radio
        self.todoRadio_1.toggled.connect(lambda: self.change_current_doing(1))
        self.todoRadio_2.toggled.connect(lambda: self.change_current_doing(2))
        self.todoRadio_3.toggled.connect(lambda: self.change_current_doing(3))
        self.todoRadio_4.toggled.connect(lambda: self.change_current_doing(4))
        self.todoRadio_5.toggled.connect(lambda: self.change_current_doing(5))

    def change_current_doing(self, i=1):
        todo_content = getattr(self, f'todoText_{i}')
        todo_content = todo_content.text()
        spacing_length = 18 - len(todo_content)
        spacing = ' ' * spacing_length if spacing_length > 0 else '         '

        with open('log/currently_doing.txt', 'w+', encoding="utf-8") as f:
            f.write(todo_content+spacing)

    def default_todo(self):
        target_lineEdit = getattr(self, 'todoText_1')
        target_checkbox = getattr(self, 'todo_1')
        target_checkbox.setChecked(False)
        target_lineEdit.setText('행정업무 TA stuff etc.')


    def timer_reset(self):
        self.timerEdit.setTime(QTime(19, 10, 00))
        self.session_count_lineEdit.setText('5')
        self.study_length_lineEdit.setText('50')
        self.break_length_lineEdit.setText('10')

    def timer_to_now(self):
        self.timerEdit.setTime(QTime.currentTime())

    def todo_load(self):
        if not os.path.isfile('log/todolist.txt'):
            return
        with open('log/todolist.txt', 'r', encoding="utf-8") as f:
            lines = f.readlines()
            for index, line in enumerate(lines[1:-1]):
                file_todo_state = line[0]
                file_todo_content = line[3:].strip()
                
                app_todo_state = getattr(self, f'todo_{index+1}')
                app_todo_content = getattr(self, f'todoText_{index+1}')

                if file_todo_state == '☑':
                    app_todo_state.setChecked(True)
                else:
                    app_todo_state.setChecked(False)
                app_todo_content.setText(file_todo_content)


    def todo_update(self):
        todo_list = "                TODAY'S TODO LIST\n"
        for int in range(1,6):
            todo_state = getattr(self, f'todo_{int}')
            todo_text = getattr(self, f'todoText_{int}').text()

            if todo_state.checkState() == 2:
                todo_list += '☑  '
            else:
                todo_list += '□  '

            todo_list += f'{todo_text}\n'
        todo_list += '                                                  '

        with open('log/todolist.txt', 'w+', encoding="utf-8") as f:
            f.write(todo_list)

    def nb_start(self):
        asyncio.create_task(self.s_nb_start())

    async def s_nb_start(self):
        command = 'resource\\nowplaying.bat'
        subprocess.run(command, shell=True)
        await asyncio.sleep(0.5)



    def remove_todo(self, i=1):
        target_lineEdit = getattr(self, f'todoText_{i}')
        target_checkbox = getattr(self, f'todo_{i}')
        target_lineEdit.setText('')
        target_checkbox.setChecked(False)

        for ind in range(i+1, 7):
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

    def timer_start(self):
        # when 'start timer' button is clicked, start the timer
        current_task_set = asyncio.all_tasks()  # get all previous tasks. For killing existing timers in advance.
        if len(current_task_set) > 1:
            for t in current_task_set:
                if t._callbacks is not None:
                    print('need to kill this task')
                    print('kill it')
            asyncio.create_task(self.cancel_existing_task(current_task_set))

        countdown_list = list()
        first_session = self.timerEdit.time()
        n_of_session = int(self.session_count_lineEdit.text())
        study_length = int(self.study_length_lineEdit.text())
        break_length = int(self.break_length_lineEdit.text())
        now = QTime.currentTime()

        # update the time table
        main.by_num_of_sessions(t=n_of_session,
                                first_session_time=first_session.toPyTime(),
                                timetable_only=True,
                                study_length=study_length,
                                break_length=break_length)

        # below is for running the timer
        time_difference = now.secsTo(first_session)
        if time_difference > 0:
            countdown_list.append(f'{first_session.toString("hh:mm")}r ')
        elif time_difference < -60*50:
            return

        for i in range(n_of_session):
            study_session_end = first_session.addSecs(60*study_length*(i+1)+60*break_length*i)
            break_session_end = study_session_end.addSecs(60*break_length)
            countdown_list.append(f'{study_session_end.toString("hh:mm")} ')
            countdown_list.append(f'{break_session_end.toString("hh:mm")}r ')


        task_timer = asyncio.create_task(self.timer_task(countdown_list))

        # task_study_music = asyncio.create_task(self.music_task())



    async def timer_task(self, cd_list):
        for item in cd_list:
            item = item.strip()
            if item[-1] != 'r':
                # if study time, play lofi
                then_h, then_m = item.split(':')
                now = QTime.currentTime()
                then = QTime(int(then_h),int(then_m), 0)
                session = now.secsTo(then)
                session = session + 86400 if session < 0 else session
                task_lofi = asyncio.create_task(lofiplayer.player_wrapper(session_length=session))

            task = asyncio.create_task(main.a_countdown(item, time_table=True))
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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    asyncio.set_event_loop(qasync.QEventLoop(app))
    window = MainWindow()
    window.show()
    exit(app.exec())
