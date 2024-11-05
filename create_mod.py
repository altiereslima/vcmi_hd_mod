#!/usr/bin/env python3
#
# MIT License
# 
# Copyright (c) 2024 Laserlicht
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
import zipfile

def create_mod(in_folder, out_folder):
    lang = os.listdir(os.path.join(in_folder, "bitmap_DXT_loc_x3.pak"))[0]

    out_folder = os.path.join(out_folder, "hd_version")
    os.makedirs(out_folder, exist_ok=True)
    out_folder_translation = os.path.join(out_folder, "mods", "translation_" + lang.lower())
    os.makedirs(out_folder_translation, exist_ok=True)

    with open(os.path.join(out_folder, "mod.json"), "w") as f:
        f.write(create_mod_config())
    with open(os.path.join(out_folder_translation, "mod.json"), "w") as f:
        f.write(create_lang_mod_config(lang))

    for name, destination in { "bitmap_DXT_com_x3.pak": out_folder, "bitmap_DXT_loc_x3.pak": out_folder_translation }.items():
        with zipfile.ZipFile(os.path.join(destination, "content.zip"), mode="w") as archive:
            path = os.path.join(in_folder, name, lang if "loc" in name else "")
            for file in os.listdir(path):
                archive.writestr(os.path.splitext(file)[0] + "$3.png", open(os.path.join(path, file), "rb").read())


def create_mod_config():
    conf = {
        "author": "Ubisoft",
        "contact": "vcmi.eu",
        "description": "Extracted resources from official Heroes HD to make it usable on VCMI",
        "modType": "Graphical",
        "name": "Heroes HD (official)",
        "version": "1.0"
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)

def create_lang_mod_config(language):
    languages = {
        "CH": "chinese",
        "CZ": "czech",
        "DE": "german",
        "EN": "english",
        "ES": "spanish",
        "FR": "french",
        "IT": "italian",
        "PL": "polish",
        "RU": "russian"
    }

    conf = {
        "author": "Ubisoft",
        "contact": "vcmi.eu",
        "description": "Translated resources",
        "modType": "Translation",
        "name": "HD Localisation",
        "version": "1.0",
        "language": languages[language]
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)