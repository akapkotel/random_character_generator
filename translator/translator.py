"""
This modle translates input text from one language to other by simply
replacing original words with corresponding words of desired language.

It needs txt or xml files with all the words to read them and replace.
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
from config_loader.config_loader import load_config_from_file

PLACEHOLDER = "Translation not found!"
DICT = None
INPUTS = None


def setup_translator(files_path: str, file_name: str):
    """
    Set-up all the required data to make other functions working properly.
    This function MUST be called first, before any other functions would be
    used.

    :param files_path: str -- absolute path to the language files
    :param file_name: str -- name of the language file
    """
    print(files_path+file_name)
    if check_if_language_file_exists(files_path + file_name):
        prepare_translation_dict(files_path, file_name)


def prepare_translation_dict(files_path: str, file_name: str):
    """
    Read language file line-by-line and fill the language translation dict
    with the keys (inputs to be translated) and values (target language).

    :param files_path: str -- absolute path to the language files
    :param file_name: str -- name of the language file
    :return: dict -- hashtable made from those strings
    """
    global DICT, INPUTS
    [DICT] = load_config_from_file(files_path, file_name)
    print(DICT)
    INPUTS = DICT.keys()


def check_if_language_file_exists(file_name: str):
    """
    TODO:
    :param file_name: str -- desired language file name
    :return: bool
    """
    try:
        os.path.isfile(file_name)
        return True
    except FileNotFoundError:
        print(f"File: {file_name} does not exist!")
        return False


def translate(input_: str):
    """
    Check if input exists in current dict and return it, otherwise, return
    placeholder.

    :return: str -- input text replaced with target-language correspondent
    """
    if input_ in INPUTS:
        return DICT[input_]
    else:
        return PLACEHOLDER
