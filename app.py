from sys import argv, exit, platform
import asyncio
from qasync import QEventLoop
from os import path
from PyQt5 import QtWidgets

from initializer import WarningDialog, resource_check
from setting import MainWindow
from progress_window import OngoingWindow
import state

base_dir = path.normpath(path.expanduser('~/Documents/Study-with-me'))  # base resource directory.


if __name__ == '__main__':
    app = QtWidgets.QApplication(argv)

    # async set
    asyncio.set_event_loop(QEventLoop(app))

    # initial resources check
    resource_check_res = resource_check()

    if resource_check_res == 1:
        warning = WarningDialog()
        warning.show()

    # inquire current OS
    state.os = platform

    # launch two windows
    setting_window = MainWindow()

    ongoing_window = OngoingWindow(camera=False)
    if state.os == 'win32':
        # camera disable by default and only enable if windows
        ongoing_window = OngoingWindow(camera=True)

    # Define a custom slot to close both windows
    def close_both_windows():
        setting_window.close()
        ongoing_window.close()

    # Connect the destroyed signal of setting_window to the custom slot
    setting_window.closed.connect(close_both_windows)

    # show the two windows
    ongoing_window.show()
    setting_window.show()
    exit(app.exec_())
