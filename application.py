"""
This is a simple character generator for quick, random creation of NPC in
role-playing games etc. You can generate race, sex, name, surname, clothes,
personal items, and weapons for a characters. You can also save them to txt
file and load from it.
"""
__author__ = "akapkotel"
__copyright__ = "Copyright 2019"
__credits__ = []
__license__ = "Share Alike Attribution-NonCommercial-ShareAlike 4.0"
__version__ = "0.0.1"
__maintainer__ = "akapkotel"
__email__ = "rafal.trabski@mises.pl"
__status__ = "Development"

import random

from tkinter import *
from tkinter import messagebox as mb
from tkinter import filedialog as fd

from translator.translator import *

# constants:

TITLE = "APPLICATION_WINDOW_TITLE"
QUIT_TITLE = "QUIT_TITLE"
QUIT_DIALOG = "QUIT_DIALOG"
# paths to the directories:
PATH = os.path.dirname(os.path.abspath(__file__))
CONFIGS_PATH = PATH + "/config_files/"
PORTRAITS_PATH = PATH + "/portraits/"
CHARACTERS_PATH = PATH + "/characters/"
LANGUAGES_PATH = PATH + "/languages/"
# names of the files:
CONFIG_FILE = "config_file.txt"
LANGUAGE_FILE = "polish.txt"


class MainApplication:

    def __init__(self, master: Tk):
        """
        Initialize new application window.

        :param master: Tk instance
        """
        self.main_frame = master
        self.main_frame.title()
        self.main_frame.protocol('WM_DELETE_WINDOW', self.close_application)

    def close_application(self):
        """
        TODO: safe closing app [ ], with saving data first [ ], and dialog [ ]
        """
        if mb.askyesno(translate(QUIT_TITLE), message=translate(QUIT_DIALOG),
                       icon="question"):
            self.main_frame.destroy()


if __name__ == '__main__':
    setup_translator(LANGUAGES_PATH, LANGUAGE_FILE)
    tk = Tk()
    app = MainApplication(tk)
    tk.mainloop()


