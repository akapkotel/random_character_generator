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
__email__ = "btcuserbtc@gmail.com"

import os
import random
from functools import partial

from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd

from config_loader.config_loader import load_config_from_file
from config_files.constants.constants import *
from translator.translator import setup_translator, translate

# constants:
WINDOW_SIZE = "920x920"
# categories:
ETHNICITIES = (WHITE, BLACK, JAPANESE, CHINESE, LATINO)
SEXES = (MALE, FEMALE)
AGES = (YOUNG, ADULT, OLD)
WEIGHTS = (THIN, NORMAL, FAT)
HEIGHTS = (SHORT, AVERAGE, TALL)
types_ = {  # associations important for buttons-creation:
    ETHNICITIES: ETHNICITY,
    AGES: AGE,
    SEXES: SEX,
    WEIGHTS: WEIGHT,
    HEIGHTS: HEIGHT,
    PROFFESIONS: PROFESSION,
    WEAPONS: ARMED,
    }
# values assigned to categories:
assigned = {AGES: "years", WEIGHTS: "kilograms", HEIGHTS: "centimeters"}
# statistical distributions:
POPULATION_HEIGHT = (SHORT,)*2 + (AVERAGE,)*4 + (TALL,)
POPULATION_WEIGHT = (THIN,)*4 + (NORMAL,)*3 + (FAT,)
# paths to the directories and files:
PATH = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = PATH + "/icon.gif"
CONFIGS_PATH = PATH + "/config_files/"
PORTRAITS_PATH = PATH + "/portraits/"
CHARACTERS_PATH = PATH + "/characters/"
LANGUAGES_PATH = PATH + "/languages/"
# names of the files:
CONFIG_FILE = "config_file.txt"
CONSTANTS_FILE = "constants.py"
LANGUAGE_FILE = "polish.txt"


def pack(widget: Widget, side=None, fill=None, expand=None):
    """
    Wraps Widget with Widget.pack() method to avoid calling pack() in new lines
    after instantiating those Widgets.
    """
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
        self.pistols_list = self.load_list_from_file(PISTOLS)
        self.rifles_list = self.load_list_from_file(RIFLES)
        self.portrait = None
        self.short_desc = StringVar()  # character info
        self.description = StringVar()
        self.name = StringVar()
        self.surname = StringVar()
        self.name_and_surname = StringVar()
        self.ethnicity = StringVar()
        self.sex = StringVar()
        self.age, self.years = StringVar(), IntVar()
        self.height, self.centimeters = StringVar(), IntVar()
        self.weight, self.kilograms = StringVar(), IntVar()
        self.professions = self.load_list_from_file(PROFFESIONS)
        self.profession = StringVar()
        self.profession.set(translate(CHOOSE_PROFESSION))
        # for current character's inventory and weapons:
        self.clothes = StringVar()
        self.pockets = StringVar()
        self.weapons = StringVar()
        # hints displayed at the bottom of the window:
        self.hint = StringVar()

        self.randomize = {t: BooleanVar() for t in types_.values()}
        for bool_ in self.randomize.values(): bool_.set(True)

        # GUI:
        self.main_frame = master
        self.main_frame.geometry(WINDOW_SIZE)
        self.main_frame.title(translate(TITLE))
        self.main_frame.protocol('WM_DELETE_WINDOW', self.close_application)

        self.menubar = Menu(self.main_frame)
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label=translate(LOAD),
                                   command=self.load_character_from_file)
        self.file_menu.add_command(label=translate(SAVE),
                                   command=self.save_character_to_file)
        self.menubar.add_cascade(label=translate(FILE), menu=self.file_menu)
        self.main_frame.config(menu=self.menubar)

        self.parameters = LabelFrame(self.main_frame)
        self.parameters_desc = Label(self.parameters,
                                     text=translate(PARAMETRES_DESC),
                                     height=2,
                                     width=500,
                                     background=HINT_COLOR)
        [x.pack(side=TOP) for x in (self.parameters, self.parameters_desc)]
        self.buttons = pack(Frame(self.parameters), side=LEFT)
        self.top_buttons = pack(Frame(self.buttons), side=TOP)
        self.middle_buttons = pack(Frame(self.buttons), side=TOP)
        self.bottom_buttons = pack(Frame(self.buttons), side=TOP)

        self.ethnicity_buttons = LabelFrame(self.top_buttons,
                                            text=translate(ETHNICITY))

        self.age_buttons = LabelFrame(self.top_buttons, text=translate(AGE))
        self.sex_buttons = LabelFrame(self.top_buttons, text=translate(SEX))
        self.height_buttons = LabelFrame(self.middle_buttons,
                                         text=translate(HEIGHT))
        self.weight_buttons = LabelFrame(self.middle_buttons,
                                         text=translate(WEIGHT))
        self.profession_frame = LabelFrame(self.middle_buttons,
                                           text=translate(PROFESSION))
        self.is_armed_frame = LabelFrame(self.middle_buttons,
                                           text=translate(IS_ARMED))

        buttons = self.top_buttons.winfo_children() + \
                  self.middle_buttons.winfo_children()
        [x.pack(side=LEFT, expand=YES, fill=BOTH) for x in buttons]

        # creating and packing buttons all at once:
        categories = (ETHNICITIES, AGES, SEXES, WEIGHTS, HEIGHTS)
        for category in categories:
            # prepare buttons name:
            cat = types_[category].lower()
            buttons = cat + "_buttons"
            level = "_top" if categories.index(category) < 3 else "_bottom"
            self.__dict__[cat + level + "_buttons_list"] = []
            # actual buttons:
            for elem in category:
                b = Radiobutton(self.__dict__[buttons],
                                text=translate(elem),
                                variable=self.__dict__[cat],
                                value=elem,
                                bg=BUTTON_COLOR_OFF,
                                height=2,
                                width=len(translate(elem))+2,
                                selectcolor=BUTTON_COLOR_ON,
                                indicatoron=0)
                b.pack(side=LEFT, fill=BOTH, expand=YES)
                if category == AGES:
                    b.bind("<Button-1>", self.new_age_value)
                if category == WEIGHTS:
                    b.bind("<Button-1>", self.new_weight_value)
                if category == HEIGHTS:
                    b.bind("<Button-1>", self.new_height_value)
            # label displaying exact (numerical) value:
            if category not in (SEXES, ETHNICITIES):
                v_name = assigned[category]
                v = pack(Label(self.__dict__[buttons],
                         text="",
                         height=2,
                         width=5,
                         relief=RAISED,
                         background=LABEL_COLOR,
                         textvariable=self.__dict__[v_name]), LEFT, BOTH, YES)
            # checkbutton setting if category should be randomized:
            rb = Checkbutton(self.__dict__[buttons],
                             variable=self.randomize[types_[category]],
                             selectcolor=GOLD_COLOR,
                             onvalue=True,
                             offvalue=False)
            rb.variable = self.randomize[types_[category]]
            rb.pack(side=LEFT, fill=BOTH, expand=YES)

        # profession-choice window top-level:
        self.profession_window = Toplevel()
        self.profession_window.title(translate(PROF_CHOICE_TITLE))

        self.scrollbar = pack(Scrollbar(self.profession_window,
                                        orient=VERTICAL), side=RIGHT, fill=Y)
        self.professions_list = pack(Listbox(self.profession_window,
                                             yscrollcommand=self.scrollbar.set,
                                             height=30,
                                             width=35))
        self.scrollbar.config(command=self.professions_list.yview)
        for profession in self.professions:
            self.professions_list.insert(END, profession.title())
        self.professions_list.bind("<Button-1>", self.change_profession)

        self.profession_window.protocol('WM_DELETE_WINDOW',
                                       partial(self.close_window,
                                               self.profession_window))
        self.profession_window.withdraw()

        self.profession_btn = Button(self.profession_frame,
                                     text=self.profession.get(),
                                     bg=BUTTON_COLOR_OFF,
                                     height=2,
                                     width=len(self.profession.get())+2,
                                     command=partial(
                                                self.open_window,
                                                self.profession_window))
        self.profession_btn.pack(side=LEFT, fill=BOTH, expand=YES)
        # checkbutton:
        self.profession_boolean = Checkbutton(self.profession_frame,
                                              variable=self.randomize[PROFESSION],
                                              selectcolor=GOLD_COLOR,
                                              onvalue=True,
                                              offvalue=False)
        self.profession_boolean.variable = self.randomize[PROFESSION]
        self.profession_boolean.pack(side=LEFT, fill=BOTH, expand=YES)
        # if person is armed:
        self.is_armed_checkbutton = Checkbutton(self.is_armed_frame,
                                                variable=self.randomize[ARMED],
                                                selectcolor=GOLD_COLOR,
                                                onvalue=True,
                                                offvalue=False)
        self.is_armed_checkbutton.variable = self.randomize[ARMED]
        self.is_armed_checkbutton.pack(side=LEFT, fill=BOTH, expand=YES)

        # button used to randomize every attribute value:
        self.randomize_button = Button(self.bottom_buttons,
                                       text=translate(RANDOMIZE_CHECKED),
                                       height=2,
                                       width=33,
                                       background=GOLD_COLOR,
                                       command=self.randomize_everything
                                       )
        self.randomize_button.pack(side=RIGHT, fill=BOTH, expand=YES)

        # name and description section:
        self.result_frame = pack(LabelFrame(self.main_frame), side=TOP,
                                 fill=BOTH)
        self.result_desc = pack(Label(self.result_frame,
                                      text=translate(RESULT_DESC),
                                      height=2,
                                      width=500,
                                      background=HINT_COLOR), side=TOP)

        self.name_l_frame = LabelFrame(self.result_frame,
                                       text=translate(NAME, AND, SURNAME)+":")
        self.name_l_frame.pack(side=LEFT, fill=Y)
        self.name_label = pack(Label(self.name_l_frame, text="",
                                     font=("Helvetica", 16),
                                     height=2,
                                     width=20,
                                     relief=SUNKEN,
                                     background=LABEL_COLOR,
                                     textvariable=self.name_and_surname), TOP)

        self.name_buttons = pack(LabelFrame(self.name_l_frame,
                                            relief=FLAT,
                                            text=translate(NEW)+":"), side=TOP)

        # name generator's buttons:
        self.r_n_btn = Button(self.name_buttons,
                              text=translate(NAME),
                              command=partial(self.new_name, 1))
        self.r_s_btn = Button(self.name_buttons,
                              text=translate(SURNAME),
                              command=partial(self.new_name, 2))
        self.r_b_btn = Button(self.name_buttons,
                              text=translate(BOTH_NAMES),
                              command=partial(self.new_name, 1, 2))
        [b.pack(side=LEFT) for b in (self.r_n_btn, self.r_s_btn, self.r_b_btn)]

        # Portrait section:
        self.portrait = self.load_image_from_file(BASIC_PORTRAIT)
        self.portrait_frame = pack(LabelFrame(self.result_frame,
                                              text=translate(PORTRAIT)),
                                   side=LEFT, expand=YES, fill=BOTH)
        self.photo_label = pack(Label(self.portrait_frame,
                                      compound=BOTTOM,
                                      width=150,
                                      height=150,
                                      borderwidth=1,
                                      relief=SUNKEN,
                                      image=self.portrait))
        self.photo_label.bind("<Button-1>", self.open_image)

        # descriptions section:
        self.short_desc_frame = pack(LabelFrame(self.result_frame,
                                     text=translate(DESCRIPTION)+":"))
        self.short_desc_label = pack(Label(self.short_desc_frame,
                                           relief=SUNKEN,
                                           width=60,
                                           height=7,
                                           wraplength=600,
                                           textvariable=self.short_desc,
                                           background=LABEL_COLOR), side=TOP)

        self.full_desc_button = pack(Button(self.short_desc_frame,
                                            text=translate(LONG_DESCRIPTION),
                                            height=1,
                                            bg=BUTTON_COLOR_OFF,
                                            command=self.show_full_description)
                                     , side=LEFT, fill=BOTH, expand=YES)
        # description-editing top-level:
        self.desc_edit_window = Toplevel()
        self.desc_edit_window.title(translate(EDIT))
        self.edit_entry = pack(Text(self.desc_edit_window,
                                    height=7,
                                    width=60,
                                    wrap=WORD,
                                    background=LABEL_COLOR), side=TOP)
        self.desc_edit_window.protocol('WM_DELETE_WINDOW',
                                       partial(self.close_window,
                                               self.desc_edit_window,
                                               self.edit_entry))
        self.desc_edit_window.withdraw()
        #   button to accept changes:
        self.save_edit_button = pack(Button(self.desc_edit_window,
                                            text=translate(SAVE),
                                            height=1,
                                            bg=GREEN_COLOR,
                                            command=partial(
                                                self.save_changes,
                                                self.edit_entry,
                                                self.short_desc)),
                                     side=RIGHT)
        #   button to cancel edits:
        self.edit_cancel_button = pack(Button(self.desc_edit_window,
                                              text=translate(CANCEL),
                                              height=1,
                                              bg=RED_COLOR,
                                              command=partial(
                                                  self.close_window,
                                                  self.desc_edit_window,
                                                  self.edit_entry)),
                                       side=RIGHT)
        #   button to show above window:
        self.edit_desc_button = pack(Button(self.short_desc_frame,
                                            text=translate(EDIT),
                                            height=1,
                                            bg=BUTTON_COLOR_OFF,
                                            command=partial(
                                                self.open_window,
                                                self.desc_edit_window)),
                                     side=LEFT, fill=BOTH, expand=YES)

        # clothes section:
        self.clothes_frame = pack(LabelFrame(self.main_frame,
                                             text=translate(CLOTHES)+":"
                                             ), side=TOP, fill=BOTH)
        self.clothes_label = pack(Label(self.clothes_frame,
                                        relief=SUNKEN,
                                        width=120,
                                        height=8,
                                        wraplength=1200,
                                        textvariable=self.clothes,
                                        background=LABEL_COLOR))
        # inventory section:
        self.pockets_frame = pack(LabelFrame(self.main_frame,
                                             text=translate(POCKETS)+":"
                                             ), side=TOP, fill=BOTH)
        self.pockets_label = pack(Label(self.pockets_frame,
                                        relief=SUNKEN,
                                        width=120,
                                        height=8,
                                        wraplength=1200,
                                        text=translate(TAKE_LOOK)+"...",
                                        background=GRAY_COLOR))
        self.pockets_label.bind("<Enter>", self.show_pockets)
        self.pockets_label.bind("<Leave>", self.hide_pockets)
        # weapons section:
        self.weapons_frame = pack(LabelFrame(self.main_frame,
                                             text=translate(WEAPONS)+":"
                                             ), side=TOP, fill=BOTH)
        self.weapons_label = pack(Label(self.weapons_frame,
                                        relief=SUNKEN,
                                        width=120,
                                        height=8,
                                        wraplength=1200,
                                        text=translate(TAKE_LOOK)+"...",
                                        background=GRAY_COLOR))
        self.weapons_label.bind("<Enter>", self.show_weapons)
        self.weapons_label.bind("<Leave>", self.hide_weapons)

        self.randomize_everything()

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

    @staticmethod
    def display_hint(field: StringVar, hint: str = "", event=Event):
        """"""
        field.set(hint)

    def bind_hint(self, widget: Widget, hint: str):
        """
        Bind Widget with a hint displayed in hint-field at the bottom of
        Window when mouse-cursor is above the Widget.

        :param widget: Tk.Widget -- element to bind with the hint
        :param hint: str -- text of the hint to be displayed
        """
        if hint is not None:
            widget.bind("<Enter>", partial(self.display_hint, hint))
            widget.bind("<Leave>", partial(self.display_hint, ""))

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

    def randomize_everything(self):
        """"""
        if self.randomize[ETHNICITY].get():
            self.ethnicity.set(random.choice(ETHNICITIES))
        if self.randomize[SEX].get():
            self.sex.set(random.choice(SEXES))
        if self.randomize[AGE].get():
            self.age.set(random.choice(AGES))
            self.new_age_value()
        if self.randomize[HEIGHT].get():
            self.height.set(random.choice(POPULATION_HEIGHT))
            self.new_height_value()
        if self.randomize[WEIGHT].get():
            self.weight.set(random.choice(POPULATION_WEIGHT))
            self.new_weight_value()
        if self.randomize[PROFESSION].get():
            self.get_random_profession()
        if self.randomize[ARMED].get():
            self.weapons.set(self.get_random_weapon(PROFESSION))
        self.new_name(1, 2)

    def new_age_value(self, event=None):
        self.years.set(self.random_gaussian(self.age.get()))

    def new_height_value(self, event=None):
        self.centimeters.set(self.random_gaussian(self.height.get()))

    def new_weight_value(self, event=None):
        cm = self.centimeters.get()
        self.kilograms.set(self.random_gaussian(self.weight.get(), cm))

    def show_pockets(self, event):
        self.pockets_label.configure(text=self.pockets.get(),
                                     background=LABEL_COLOR)

    def hide_pockets(self, event):
        self.pockets_label.configure(text=translate(TAKE_LOOK)+"...",
                                     background=GRAY_COLOR)

    def show_weapons(self, event):
        self.weapons_label.configure(text=self.weapons.get(),
                                     background=LABEL_COLOR)

    def hide_weapons(self, event):
        self.weapons_label.configure(text=translate(TAKE_LOOK)+"...",
                                     background=GRAY_COLOR)

    def get_random_profession(self):
        profession_index = random.choice(range(len(self.professions)))
        self.profession.set(self.professions[profession_index])
        self.profession_btn.config(text=self.profession.get().title())
        self.professions_list.current = profession_index

    def get_random_weapon(self, profession: str):
        """

        :param profession: str --
        :return: str
        """
        weapons = ""
        weapons += random.choice(self.pistols_list) + "\n\n"
        weapons += random.choice(self.rifles_list)
        return weapons

    def change_profession(self, event):
        profession = self.professions_list.get(ACTIVE)
        self.profession.set(profession)
        self.profession_btn.configure(text=profession)

    @staticmethod
    def random_gaussian(parameter: str, cm: int = 0):
        """
        Calculate random value for required trait range from categories such
        us: WEIGHT, HEIGHT and AGE using gaussian distribution.

        :param parameter: str -- name of the trait to be calculated, could be:
        YOUNG, ADULT, OLD, or: SHORT, AVERAGE, TALL, or: THIN, NORMAL, FAT.
        :param cm: int -- height of character in centimetres (required only to
         correctly calculate weight)
        :return: int -- random value calculated with gaussian distribution
        """
        params = {YOUNG: (20, 4), ADULT: (35, 5), OLD: (55, 5),
                  SHORT: (150, 10), AVERAGE: (175, 10), TALL: (190, 10),
                  THIN: (cm-110, 5), NORMAL: (cm-95, 5), FAT: (cm-80, 5)}
        mean, deviation = params[parameter][0], params[parameter][1]
        return int(random.gauss(mean, deviation))

    @staticmethod
    def convert_units(value: int, target: str):
        """
        Convert value from one unit to another.

        :param value: int -- value in the unit from which you want to convert
        :param target: str -- name of the targeted unit: "CM", "INCH", "KG",
         "FEET" or "IBS"
        :return: int -- value in targeted units
        """
        rates = {"CM": 2.54, "INCH": 0.44, "KG": 0.45, "IBS": 2.2,
                 "FEET": 30.48}
        return value * rates[target]

    @staticmethod
    def open_window(window: Toplevel):
        """TODO"""
        window.deiconify()
        window.grab_set()
        window.focus_set()

    @staticmethod
    def save_changes(text: Text, attribute: StringVar or IntVar):
        """TODO"""
        if text.get(1.0, END) is not None:
            attribute.set(text.get(1.0, END))

    def show_full_description(self):
        """TODO"""
        raise NotImplementedError

    @staticmethod
    def close_window(window: Toplevel, *widgets):
        """TODO"""
        for widget in widgets:
            if isinstance(widget, Text):
                widget.delete(1.0, END)
            elif isinstance(widget, Listbox):
                widget.delete(0, END)
        window.grab_release()
        window.withdraw()

    def open_image(self, event):
        """
        TODO: image choice by user [x], setting chosen image as
         self.portrait [x], updating self.photo_label [x]
        """
        img = fd.askopenfile(initialdir=PORTRAITS_PATH,
                             title=translate(ASK_OPEN_IMAGE),
                             filetypes=())
        if img:
            path_and_file = img.name.rpartition("/")
            self.portrait = self.load_image_from_file(path_and_file[2],
                                                      path_and_file[0] +
                                                      path_and_file[1])
            self.photo_label.configure(image=self.portrait)

    @staticmethod
    def load_image_from_file(file_name: str, file_path: str = None):
        """
        TODO: checking if file exists [x], loading it [x], loading
         placeholder image instead if requested does not exist [x]
        :return:
        """
        path = file_path if file_path is not None else PORTRAITS_PATH
        try:
            os.path.isfile(PORTRAITS_PATH+file_name)
            portrait = PhotoImage(file=path + file_name)
        except FileNotFoundError:
            print(f"Image {file_name} does not exist!")
            portrait = PhotoImage(file=path + BASIC_PORTRAIT)
        return portrait

    def load_character_from_file(self):
        """
        TODO: dialog for user for file choice [ ], search for file [ ] read [ ]
        :return:
        """
        file = fd.askopenfile(initialdir=CHARACTERS_PATH,
                              title=translate(ASK_OPEN_TITLE),
                              filetypes=())
        if file:
            with open(file.name, "r") as file:
                data = file.readlines()
                categories = (self.name_and_surname, self.ethnicity, self.sex,
                              self.age, self.years, self.weight,
                              self.kilograms, self.height, self.centimeters,
                              self.short_desc, self.description, self.clothes,
                              self.pockets, self.weapons)

                for i in range(len(data)):
                    if isinstance(categories[i], IntVar):
                        categories[i].set(int(data[i].split(" = ")[1]))
                    else:
                        categories[i].set(data[i].split(" = ")[1])

    def save_character_to_file(self):
        """
        Find character-sheets dir, open or create new file named as current
        character, edit it to fill with current data and close it.
        """
        try:
            os.path.isdir(CHARACTERS_PATH)
            file_path = CHARACTERS_PATH
            file_name = str(self.name_and_surname.get())+".txt"
            with open(file_path + file_name, "w") as file:
                categories = (NAME, ETHNICITY, SEX, AGE, "Years", WEIGHT,
                              KILOGRAMS, HEIGHT, CENTIMETERS, "short_desc",
                              "description", CLOTHES, WEAPONS)
                values = (self.name_and_surname, self.ethnicity, self.sex,
                          self.age, self.years, self.weight, self.kilograms,
                          self.height, self.centimeters, self.short_desc,
                          self.description, self.clothes, self.pockets,
                          self.weapons)
                for i in range(len(categories)):
                    line = categories[i].lower() + " = " + str(values[i].get())
                    file.write(line + "\n")
        except NotADirectoryError:
            print(f"Directory {CHARACTERS_PATH} does not exist")

    @staticmethod
    def load_list_from_file(category: str):
        """
        Load simple list of string names from txt file sorted alphabetically to
        be used by random generators or profession-choice window.

        :param category: str -- type of items to be loaded, could be one of
        constants: PROFESSIONS, WEAPONS, ITEMS
        :return: list -- sorted alphabetically
        """
        try:
            os.path.isdir(CONFIGS_PATH)
            file_path = CONFIGS_PATH
            file_name = category.lower() + ".txt"
            items = open(file_path + file_name, "r").readlines()[0].strip("\n")
            list_of_items = items.split(", ")
            list_of_items.sort()
            return list_of_items
        except NotADirectoryError:
            print(f"Directory {CONFIGS_PATH} does not exist")

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
    icon = PhotoImage(file=ICON_PATH)
    tk.call('wm', 'iconphoto', tk._w, icon)
    app = MainApplication(tk)
    tk.mainloop()
