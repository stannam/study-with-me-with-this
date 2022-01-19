# import the time module
import time
import asyncio
import os
import pyglet
import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QDialog, QApplication
from MainWindow import Ui_MainWindow


#  class AppWindow(QDialog):
#      def __init__(self):
#          super().__init__()
#          self.ui = Ui_MainWindow()
#          self.ui.setupUi(self)
#          self.show()

# define the countdown func.
def countdown(t, breaktime=False, time_table=False):
    '''
    updates the timer.

    :param t: str in time format e.g., 12:34 or in time format plus 'r' e.g., 12:34r
    :param breaktime: Bool. whether break time or study time.
    :param time_table: Bool. whether time_table is printed.
    :return: False
    '''
    if t[-1].isalpha():
        t, breaktime = t[:-1], t[-1]

    try:
        target_time = [int(i) for i in t.split(':')]
    except ValueError:
        return True

    current_time = datetime.now()
    next_day = False

    if len(target_time) == 1:
        return True
    if target_time[0] < 13 and (current_time.hour - target_time[0]) > 0:
        target_hour = target_time[0] + 12
        if target_hour < current_time.hour:    # if target time refers to the next day
            next_day = True
            target_hour -= 12
    else:
        target_hour = target_time[0]
    target_min = target_time[1]

    try:
        target_second = target_time[2]
    except IndexError:
        target_second = 0

    try:
        target_time = current_time.replace(hour=target_hour, minute=target_min, second=target_second)
        if next_day:
            target_time += timedelta(days=1)
    except ValueError or OverflowError:
        return True

    diffsec = int((target_time - current_time).total_seconds())

    file_name = '[BREAK]_TIME.txt' if breaktime else '[STUDY]_DOWN.txt'

    timer_path = os.path.join(os.getcwd(), 'log', file_name)
    while diffsec:
        diffsec = int((target_time - datetime.now()).total_seconds())
        if diffsec < 0:
            diffsec = 0

        mins, secs = divmod(diffsec, 60)
        hours, mins = divmod(mins, 60)
        timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

        with open(timer_path, "w+", encoding='utf-8-sig') as f:  # print timer
            f.write(timer)

        if time_table:              # update timetable
            update_timetable()

        time.sleep(0.5)

    # play the bell if the time is up
    ring_bell()

    return False

# async countdown function. this needs to be cleaned
async def a_countdown(input_t, breaktime=False, time_table=False):
    '''
    updates the timer.

    :param t: str in time format e.g., 12:34 or in time format plus 'r' e.g., 12:34r
    :param breaktime: Bool. whether break time or study time.
    :param time_table: Bool. whether time_table is printed.
    :return: False
    '''
    if input_t[-1].isalpha():
        t, breaktime = input_t[:-1], input_t[-1]
        print(f'breaktime until {t}')
    else:
        print(f'input_t:{input_t} \n input_t[-1]: {input_t[-1]}')
        t = input_t

    try:

        target_time = [int(i) for i in t.split(':')]
    except ValueError:
        print(f'timer didnt start with {t}')
        return True

    current_time = datetime.now()
    next_day = False

    if len(target_time) == 1:
        return True
    if target_time[0] < 13 and (current_time.hour - target_time[0]) > 0:
        target_hour = target_time[0] + 12
        if target_hour < current_time.hour:    # if target time refers to the next day
            next_day = True
            target_hour -= 12
    else:
        target_hour = target_time[0]
    target_min = target_time[1]

    try:
        target_second = target_time[2]
    except IndexError:
        target_second = 0

    try:
        target_time = current_time.replace(hour=target_hour, minute=target_min, second=target_second)
        if next_day:
            target_time += timedelta(days=1)
    except ValueError or OverflowError:
        return True

    diffsec = int((target_time - current_time).total_seconds())

    file_name = '[BREAK]_TIME.txt' if breaktime else '[STUDY]_DOWN.txt'

    timer_path = os.path.join(os.getcwd(), 'log', file_name)
    while diffsec:
        diffsec = int((target_time - datetime.now()).total_seconds())
        if diffsec < 0:
            diffsec = 0

        mins, secs = divmod(diffsec, 60)
        hours, mins = divmod(mins, 60)
        timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

        with open(timer_path, "w+", encoding='utf-8-sig') as f:  # print timer
            f.write(timer)
        if time_table:              # update timetable
            update_timetable()
        # print(f'input_t:{input_t}\ntarget:{target_time}\ncurrenttime:{datetime.now()}\ntimer:{timer}\n------\n')
        await asyncio.sleep(0.5)
    # play the bell if the time is up
    ring_bell()

    return False

def update_timetable():
    # read timetable list as list. if fails, just return True
    try:
        tt_list = []
        with open('./log/timetable.txt', encoding='utf-8-sig') as tt:
            for line in tt:
                tt_list.append(line.strip())
    except FileNotFoundError:
        return True

    # read html file and see where is the highlight
    highlight_loc = 0
    try:
        html_list = []
        with open('./log/timetable.html', encoding='utf-8-sig') as html:
            for line in html:
                html_list.append(line.strip())
        where_is_highlight = html_list[2].split('<tr')
        for ind, highlight in enumerate(where_is_highlight):
            if 'highlighted' in highlight:
                highlight_loc = ind
                break
    except FileNotFoundError:
        write_html(tt_list)

    for string in html_list[2].split():
        if ':' in string:
            first_session_start = datetime.now().replace(hour=int(string.split(':')[0]),
                                                         minute=int(string.split(':')[1]),
                                                         second=0)
            if (datetime.now() - first_session_start).total_seconds() ** 2 > 3600 ** 2:
                write_html(tt_list)
            break

    for ind, tt_line in enumerate(tt_list):
        session_start_time, session_end_time = get_start_end_times(tt_line=tt_line)

        if session_start_time <= datetime.now() <= session_end_time and highlight_loc != ind+1:
            write_html(tt_list)
            break


def write_html(tt_list):
    try:
        meta_data = open('./log/tb_metadata.txt', 'r', encoding='utf-8-sig')
        lines = meta_data.readlines()
        meta_data.close()

    except FileNotFoundError:
        lines = ['<!DOCTYPE html>\n', '<html><head>'
                                      # '<meta http-equiv="refresh" content="5">'
                                      '<style>body {background-color: rgba(24, 24, 24, 255);'
                                      'font-family: \'NanumSquare\', serif}'
                                      'table {border: 0px;font-size: 30px;font-weight: bold;text-align: left;'
                                      'width: 100%;border-spacing: 0;padding: 0px;white-space:pre}tr {color: white;}'
                                      'tr.highlighted {background-color: white; color: black;}'
                                      '</style></head><body>'
                                      '<script type="text/javascript" src="refresh.js"></script>'
                                      '<table>', '</table></body></html>']
        meta_data = open('./log/tb_metadata.txt', 'w+', encoding='utf-8-sig')
        meta_data.writelines(lines)
        meta_data.close()

    header = lines[0:2]
    tail = lines[2]

    lines.append(''.join(header))
    for tt_line in tt_list:
        session_start_time, session_end_time = get_start_end_times(tt_line)

        if session_start_time <= datetime.now() <= session_end_time:
            lines.append("<tr class='highlighted'><td>")
        else:
            lines.append("<tr><td>")
        lines.append(tt_line + '</td></tr>')
    lines.append(tail)

    with open('./log/timetable.html', 'w+', encoding='utf-8-sig') as tt_html:
        tt_html.writelines(lines)


def by_num_of_sessions(t, first_session_time=None, timetable_only=False, study_length=50, break_length=10):
    # this function converts start time and number of study sessions into timetable and timer settings.
    # t = number of sessions, start_time is time.

    # start_time is the time when the first session starts. It should be fixed since it needs to be referred later.
    start_time = datetime.now()
    if start_time.minute < 30:
        start_time = start_time.replace(minute=0, second=0)
    else:
        start_time = start_time.replace(minute=30, second=0)
    try:
        t = int(t)
    except ValueError:
        return True

    if first_session_time is not None:
        start_time = start_time.replace(hour=first_session_time.hour, minute=first_session_time.minute, second=0)



    timetable = list()
    list_for_countdown = list()

    for t_session in range(t):
        study_end_minutes = study_length * (t_session + 1) + break_length * t_session

        # study_start and study_end are variables for each session.
        study_end = start_time + timedelta(minutes=study_end_minutes)
        break_end = study_end + timedelta(minutes=break_length)
        study_start = study_end - timedelta(minutes=study_length)

        study_start_str = f"{study_start.hour:02d}" + ':' + f"{study_start.minute:02d}"
        study_end_str = f"{study_end.hour:02d}" + ':' + f"{study_end.minute:02d}"
        break_end_str = f"{break_end.hour:02d}" + ':' + f"{break_end.minute:02d}"

        timetable.append(str(f'  {t_session + 1}    {study_start_str}   -   {study_end_str}    {study_length}m  '))
        list_for_countdown.append(study_end_str)
        list_for_countdown.append(break_end_str + 'r')
    timetable_path = os.path.join(os.getcwd(), 'log', 'timetable.txt')

    with open(timetable_path, "w", encoding='utf-8-sig') as f:
        for line in timetable:
            f.write(line+'\n')

    write_html(tt_list=timetable)

    if timetable_only:
        return

    # if the first study session is expected to be longer than 50mins, start with break time
    if start_time > datetime.now():
        list_for_countdown = [str(start_time.hour) + ':' + str(start_time.minute + 5) + 'r'] + list_for_countdown

    [countdown(item, time_table=True) for item in list_for_countdown]


def ring_bell():
    bell_path = '.\\resource\\sound\\bell1.mp3'

    # ring bell using pygame
    # pygame.mixer.init()
    # bellObj = pygame.mixer.Sound(bell_path)
    # bellObj.play()
    # time.sleep(bellObj.get_length)

    # ring bell using pyglet
    bell = pyglet.media.Player()
    x = pyglet.media.load(bell_path, streaming=False)
    bell.queue(x)
    bell.play()
    time.sleep(x.duration)


def get_start_end_times(tt_line):
    """
    :param tt_line: str. a line from timetable txt file that looks like "1   00:10 - 01:00 50m"
    :return: tuple of start and end time (each timedate object)
    """
    session_start_str = tt_line.split()[1]
    session_end_str = tt_line.split()[3]
    session_start_time = datetime.now().replace(hour=int(session_start_str.split(':')[0]),
                                                minute=int(session_start_str.split(':')[1]),
                                                second=0)
    session_end_time = datetime.now().replace(hour=int(session_end_str.split(':')[0]),
                                              minute=int(session_end_str.split(':')[1]),
                                              second=0)

    if (datetime.now() - session_start_time).total_seconds() ** 2 > (60 * 60 * 12) ** 2:
        session_start_time += timedelta(days=1)

    if datetime.now() > session_end_time:
        session_end_time += timedelta(days=1)
        if (session_end_time - session_start_time).total_seconds() > 7200:
            session_end_time -= timedelta(days=1)

    return (session_start_time, session_end_time)


def main(args, t=' '):
    print(args)
    if len(args) == 2:
        try:
            by_num_of_sessions(int(args[1]))
        except ValueError:
            pass

    while t:
        if t == ' ':
            t = input("Enter an end time (e.g., 20:00). Use the suffix 'r' for recess.... "
                      "'q' for exit. '?' for help: ")
        if t.lower() == 'q':
            break
        if t == 'b':
            ring_bell()
            t = ' '
        elif t == '?':
            print("Type 'b' for bell test. Type '20:00r' for a break timer that ends at 20:00.\n"
                  "Type an integer e.g., 5 to start five 50-10 pomodoro sessions.\n"
                  "Force end the program by hitting 'Ctrl + C' on Windows or 'Cmd + . (dot/period)' on Mac.")
            t = ' '
        elif ':' not in t:
            by_num_of_sessions(t)
        else:
            for t_each in t.split(' '):
                countdown(t_each)
                t = False


# function call
if __name__ == '__main__':
    main(args=sys.argv)
