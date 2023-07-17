# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from colored import Fore, Back, Style

class TextComponent:
    def __init__(self, text, **kwargs) -> None:
        defaults = {
            "bold": False,
            "italic": False,
            "underlined": False,
            "strikethrough": False,
            "obfuscated": False,
            "color": "white",
        }
        self.args = {**defaults, **kwargs}
        self.text = text
    
    def render(self):
        bold = Style.BRIGHT if self.args["bold"] else ""
        italic = Style.ITALIC if self.args["italic"] else ""
        underlined = Style.UNDERLINE if self.args["underlined"] else ""
        strikethrough = Style.STRIKETHROUGH if self.args["strikethrough"] else ""
        obfuscated = Style.BLINK if self.args["obfuscated"] else ""
        color = Fore.__dict__[self.args["color"].upper()]

        return f"{bold}{italic}{underlined}{strikethrough}{obfuscated}{color}{self.text}"

class ChatParser:
    @staticmethod
    def parse(text):
        parsed_text = ""

        for item in text:
            raw = item["text"]
            if "extra" in item:
                parsed_text += ChatParser.parse(item["extra"])
            parsed_text += TextComponent(raw, **item).render()
