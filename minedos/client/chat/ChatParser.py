# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from colored import Fore, Style
import json

class TextComponent:
    __color_table = {
        "black": Fore.BLACK,
        "dark_blue": Fore.BLUE,
        "dark_green": Fore.GREEN,
        "dark_aqua": Fore.CYAN,
        "dark_red": Fore.RED,
        "dark_purple": Fore.MAGENTA,
        "gold": Fore.YELLOW,
        "gray": Fore.WHITE,
        "dark_gray": Fore.BLACK,
        "blue": Fore.BLUE,
        "green": Fore.GREEN,
        "aqua": Fore.CYAN,
        "red": Fore.RED,
        "light_purple": Fore.MAGENTA,
        "yellow": Fore.YELLOW,
        "white": Fore.WHITE
    }

    def __init__(self, **kwargs) -> None:
        defaults = {
            "bold": False,
            "italic": False,
            "underlined": False,
            "strikethrough": False,
            "obfuscated": False,
            "color": "white",
            "translate": None,
            "text": ""
        }
        self.args = {**defaults, **kwargs}
    
    def __get_translatable_textcomp(self, language, key):
        translation_table = json.load(open(f"lang/{language}.json"))
        return translation_table[key]
    
    def render(self, lang="en_us"):
        bold = Style.BRIGHT if self.args["bold"] else ""
        italic = Style.ITALIC if self.args["italic"] else ""
        underlined = Style.UNDERLINE if self.args["underlined"] else ""
        strikethrough = Style.STRIKETHROUGH if self.args["strikethrough"] else ""
        obfuscated = Style.BLINK if self.args["obfuscated"] else ""
        
        color = "white"
        if color in self.__color_table:
            color = self.__color_table[self.args["color"]]
        
        if self.args["translate"]:
            self.args["text"] = self.__get_translatable_textcomp(lang, self.args["translate"])

        return f"{bold}{italic}{underlined}{strikethrough}{obfuscated}{color}{self.args['text']}"

class ChatParser:
    @staticmethod
    def parse(text):
        parsed_text = ""
        if "extra" in text:
            for subitem in text["extra"]:
                parsed_text += ChatParser.parse(subitem)
        parsed_text += TextComponent(**text).render()
        return parsed_text
