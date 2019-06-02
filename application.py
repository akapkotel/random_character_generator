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

import os
import random
from functools import partial

from tkinter import *
from tkinter import messagebox as mb
from tkinter import filedialog as fd

from config_loader.config_loader import load_config_from_file
from config_files.constants.constants import *
from translator.translator import setup_translator, translate

# constants:
WINDOW_SIZE = "800x800"
ETHNICITIES = (WHITE, BLACK, JAPANESE, CHINESE, LATINO)
SEXES = (MALE, FEMALE)
AGES = (YOUNG, ADULT, OLD)
# paths to the directories:
PATH = os.path.dirname(os.path.abspath(__file__))
CONFIGS_PATH = PATH + "/config_files/"
PORTRAITS_PATH = PATH + "/portraits/"
CHARACTERS_PATH = PATH + "/characters/"
LANGUAGES_PATH = PATH + "/languages/"
# names of the files:
CONFIG_FILE = "config_file.txt"
CONSTANTS_FILE = "constants.py"
LANGUAGE_FILE = "polish.txt"


def pack(widget: Widget, side=None, fill=None, expand=None):
    widget.pack(side=side, fill=fill, expand=expand)
    return widget


class MainApplication:
    """Tkinter application."""

    def __init__(self, master):
        """
        Initialize new application window.

        :param master: Tk instance
        """
        # two dicts will keep names and surnames for all sexes and races:
        self.names = self.load_names()
        self.surnames = self.load_surnames()
        self.portrait = None  # for the character's portrait, if has one
        self.name = StringVar()
        self.surname = StringVar()
        self.name_and_surname = StringVar()
        self.ethnicity = StringVar()
        self.sex = StringVar()
        self.age = StringVar()
        self.height = StringVar()
        # hints displayed at the bottom of the window:
        self.hint = StringVar()

        self.main_frame = master
        self.main_frame.geometry(WINDOW_SIZE)
        self.main_frame.title(translate(TITLE))
        self.main_frame.protocol('WM_DELETE_WINDOW', self.close_application)

        self.parameters = LabelFrame(self.main_frame,
                                     text=translate(PARAMETRES))
        self.parameters_desc = Label(self.parameters,
                                     text=translate(PARAMETRES_DESC),
                                     height=2,
                                     width=500,
                                     background=HINT_COLOR)
        [x.pack(side=TOP) for x in (self.parameters, self.parameters_desc)]
        self.buttons = pack(Frame(self.parameters), side=LEFT)

        self.ethnicity_buttons = LabelFrame(self.buttons, text=translate(
            ETHNICITY))
        self.age_buttons = LabelFrame(self.buttons, text=translate(AGE))
        self.sex_buttons = LabelFrame(self.buttons, text=translate(SEX))
        [x.pack(side=LEFT) for x in self.buttons.winfo_children()]

        # creating and packing buttons all at once:
        types_ = {ETHNICITIES: ETHNICITY, AGES: AGE, SEXES: SEX}
        for category in (ETHNICITIES, AGES, SEXES):
            # set random sex, age and ethnicity at the start:
            self.__dict__[types_[category].lower()].set(random.choice(category))
            # prepare buttons name:
            cat = types_[category].lower() + "_buttons"
            self.__dict__[cat + "_list"] = []
            # actual buttons:
            for elem in category:
                b = self.make_button(self.__dict__[cat], translate(elem))
                b.configure(command=partial(self.set_trait, b, elem))
                b.pack(side=LEFT, fill=BOTH, expand=YES)
                self.__dict__[cat + "_list"].append(b)
        # name frame:
        self.result_frame = pack(Frame(self.main_frame), side=TOP)

        self.name_l_frame = LabelFrame(self.result_frame,
                                       text=translate(NAME, AND, SURNAME))
        self.name_b_frame = Frame(self.result_frame)

        self.name_label = Label(self.name_l_frame, text="",
                                height=2,
                                width=20,
                                relief=SUNKEN,
                                background=LABEL_COLOR,
                                textvariable=self.name_and_surname)

        for x in (self.name_l_frame, self.name_b_frame, self.name_label):
            x.pack(side=LEFT)
        # name generator's buttons:
        self.random_name_btn = self.make_button(self.name_b_frame,
            text=translate(NEW_NAME), function_=partial(self.new_name, 1))
        self.random_surname_btn = self.make_button(self.name_b_frame,
            text=translate(NEW_SURNAME), function_=partial(self.new_name, 2))
        self.random_both_btn = self.make_button(self.name_b_frame,
            text=translate(NEW_BOTH), function_=partial(self.new_name, 1, 2))

        self.portrait = self.load_image_from_file(BASIC_PORTRAIT)
        self.photo_label = pack(Label(self.main_frame, text="",
                                      image=self.portrait), LEFT)

    @staticmethod
    def load_surnames():
        """
        Unpack surnames from txt file and put them into the internal dict for
        future use.

        :return: dict
        """
        dict_ = {}
        file_name = "surnames.txt"
        unpacked = load_config_from_file(CONFIGS_PATH, file_name)

        for i in range(len(ETHNICITIES)):
            dict_[ETHNICITIES[i]] = unpacked[0][ETHNICITIES[i]]

        return dict_

    @staticmethod
    def load_names():
        """
        Unpack names from txt file and put them into the internal dict for
        future use.

        :return: dict
        """
        dict_ = {}

        file_name = "names.txt"
        unpacked = load_config_from_file(CONFIGS_PATH, file_name)

        for i in range(len(ETHNICITIES)):
            dict_[ETHNICITIES[i]] = unpacked[i]

        return dict_

    def make_button(self, parent: Widget,
                    text: str = "Button",
                    color: str = BUTTON_COLOR_OFF,
                    highlightcolor_: str = BUTTON_COLOR_ON,
                    tip: str = "",
                    function_: callable = None):
        """
        Wraps the tkinter Button Widget and assures that every Button created
        in the application would share the same parameters and functionalities.

        :param parent:
        :param text:
        :param color:
        :param highlightcolor_:
        :param tip:
        :param function_:
        :return: tk.Button
        """
        button = Button(parent, text=text,
                        command=function_,
                        bg=color,
                        highlightcolor=highlightcolor_)
        if tip is not None:
            button.bind("<Enter>", partial(self.display_tip, tip))
            button.bind("<Leave>", partial(self.display_tip, ""))
        button.pack()
        return button

    def display_tip(self, tip: str = "", event=Event):
        """"""
        self.hint.set(tip)

    def set_trait(self, button: Button, trait: str):
        """
        Set one of the basic traits of the current character and handle the
        state of buttons.

        :param button: Button -- button which was pressed
        :param trait: str -- value of the category which is set-up, eg. "WHITE"
        """
        categories = {MALE: SEX, FEMALE: SEX, WHITE: ETHNICITY, OLD: AGE,
                      BLACK: ETHNICITY, JAPANESE: ETHNICITY, ADULT: AGE,
                      CHINESE: ETHNICITY, LATINO: ETHNICITY, YOUNG: AGE}
        attribute = categories[trait].lower()
        self.__dict__[attribute].set(trait)
        # handle the buttons:
        for b in self.__dict__[attribute+"_buttons_list"]:
            b.configure(state=NORMAL, relief=RAISED, bg=BUTTON_COLOR_OFF)
        button.configure(state=DISABLED, relief=SUNKEN, bg=BUTTON_COLOR_ON)

    def new_name(self, *names):
        for name in names:
            if name == 1:
                self.name.set(self.name_generator())
            elif name == 2:
                self.surname.set(self.surname_generator())
        self.name_and_surname.set(self.name.get() + " " + self.surname.get())

    def name_generator(self):
        """Generate random name of required sex and ethnicity."""
        return random.choice(self.names[self.ethnicity.get()][self.sex.get()])

    def surname_generator(self):
        """Generate random surname of required ethnicity."""
        return random.choice(self.surnames[self.ethnicity.get()])

    @staticmethod
    def load_image_from_file(file_name):
        """
        TODO:
        :return:
        """
        try:
            os.path.isfile(PORTRAITS_PATH+file_name)
            portrait = PhotoImage(file=PORTRAITS_PATH + file_name)
        except FileNotFoundError:
            print(f"Image {file_name} does not exist!")
            portrait = PhotoImage(file=PORTRAITS_PATH + BASIC_PORTRAIT)
        print(portrait)
        return portrait

    def load_character_from_file(self):
        """
        TODO: dialog for user for file choice [ ], search for file [ ] read [ ]
        :return:
        """
        raise NotImplementedError

    def save_character_to_file(self):
        """
        Find character-sheets dir, open or create new file named as current
        character, edit it to fill with current data and close it.
        """
        try:
            os.path.isdir(CHARACTERS_PATH)
            with open(str(self.name_and_surname)+".txt", "w") as file:
                l = (self.name_and_surname, self.ethnicity, self.sex, self.age)
                for elem in l:
                    file.write(elem.get())
        except NotADirectoryError:
            print(f"Directory {CHARACTERS_PATH} does not exist")

    def close_application(self):
        """
        Safely close app, with saving data first after displaying dialog to
        user.
        """
        if mb.askyesno(translate(QUIT_TITLE), message=translate(QUIT_DIALOG),
                       icon="question"):
            self.main_frame.destroy()


if __name__ == '__main__':
    setup_translator(LANGUAGES_PATH, LANGUAGE_FILE)
    tk = Tk()
    app = MainApplication(tk)
    tk.mainloop()
