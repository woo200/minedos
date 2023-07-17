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
    
    def __format_mc(self, text, table):
        final_text = ""

        is_placeholder = False
        skip_next = False
        current_placeholder_num = ""

        for c in text:
            if skip_next:
                skip_next = False
                continue
            if c == "%":
                is_placeholder = True
                continue
            if is_placeholder:
                if c == "$":
                    final_text += table[int(current_placeholder_num)-1]
                    current_placeholder_num = ""
                    is_placeholder = False
                    skip_next = True
                else:
                    current_placeholder_num += c
                continue
            final_text += c
        return final_text

    def __render_translatable_textcomp(self, language, component):
        translated_text = self.__get_translatable_textcomp(language, component["translate"])

        if "with" in component:
            insertion_table = []
            for subcomponent in component["with"]:
                insertion_table.append(ChatParser.parse(subcomponent))
            translated_text = self.__format_mc(translated_text, insertion_table)
        return translated_text
        
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
            self.args["text"] = self.__render_translatable_textcomp(lang, self.args)

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
