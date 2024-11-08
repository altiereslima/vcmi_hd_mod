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
import io
import json
import zipfile
import pandas as pd
from PIL import Image

def create_mod(in_folder, out_folder, scales):
    out_folder = os.path.join(out_folder, "hd_version")
    os.makedirs(out_folder, exist_ok=True)

    df = pd.read_csv("sd_lod_sprites.csv", sep=";", header=0)

    for scale in scales:
        lang = os.listdir(os.path.join(in_folder, "bitmap_DXT_loc_x" + scale + ".pak"))[0]

        out_folder_main = os.path.join(out_folder, "mods", "x" + scale)
        os.makedirs(out_folder_main, exist_ok=True)
        out_folder_translation = os.path.join(out_folder, "mods", "x" + scale + "_translation_" + lang.lower())
        os.makedirs(out_folder_translation, exist_ok=True)

        with open(os.path.join(out_folder, "mod.json"), "w") as f:
            f.write(create_mod_config())
        with open(os.path.join(out_folder_main, "mod.json"), "w") as f:
            f.write(create_main_mod_config(scale))
        with open(os.path.join(out_folder_translation, "mod.json"), "w") as f:
            f.write(create_lang_mod_config(scale, lang))

        for name, destination in { "bitmap_DXT_com_x" + scale + ".pak": out_folder_main, "bitmap_DXT_loc_x" + scale + ".pak": out_folder_translation }.items():
            with zipfile.ZipFile(os.path.join(destination, "content.zip"), mode="w") as archive:
                path = os.path.join(in_folder, name, lang if "loc" in name else "")
                for file in os.listdir(path):
                    handle_bitmaps(archive, path, file, scale)

        for name, destination in { "sprite_DXT_com_x" + scale + ".pak": out_folder_main, "sprite_DXT_loc_x" + scale + ".pak": out_folder_translation }.items():
            with zipfile.ZipFile(os.path.join(destination, "content.zip"), mode="a") as archive:
                path = os.path.join(in_folder, name, lang if "loc" in name else "")

                grouped_df = df.groupby('defname')
                for name, group in grouped_df:
                    folders = [x.upper() for x in os.listdir(path)]
                    if name.upper() in folders:
                        folder = os.listdir(path)[folders.index(name.upper())]
                        handle_sprites(archive, path, folder, scale, group)

def handle_bitmaps(archive, path, file, scale):
    name = os.path.splitext(file)[0]

    if name.upper() in [ "MAINMENU", "GAMSELBK", "GSELPOP1", "SCSELBCK", "LOADGAME", "NEWGAME", "LOADBAR" ]:
        return

    archive.writestr("data/" + os.path.splitext(file)[0] + "$" + scale + ".png", open(os.path.join(path, file), "rb").read())

def handle_sprites(archive, path, folder, scale, df):
    data = {x:open(os.path.join(path, folder, x), "rb").read() for x in os.listdir(os.path.join(path, folder))}
    s = int(scale)

    # skip menu buttons
    if folder.upper() in ["MMENUNG", "MMENULG", "MMENUHS", "MMENUCR", "MMENUQT", "GTSINGL", "GTMULTI", "GTCAMPN", "GTTUTOR", "GTBACK", "GTSINGL", "GTMULTI", "GTCAMPN", "GTTUTOR", "GTBACK"]:
        return

    # skip water + rivers special handling - paletteAnimation
    if folder.upper() in ["WATRTL", "LAVATL"] + ["CLRRVR", "MUDRVR", "LAVRVR"]:
        return

    # resize def
    max_size_x = df["full_width"].max() * s
    max_size_y = df["full_height"].max() * s
    for item in data.keys():
        df_tmp = df[df["imagename"].str.upper() == os.path.splitext(item)[0].upper()]
        if len(df_tmp) > 0:
            df_row = df_tmp.iloc[0]
            img = Image.open(io.BytesIO(data[item]))
            tmpimg = Image.new(img.mode, (max_size_x, max_size_y), (255, 255, 255, 0))
            tmpimg.paste(img, (df_row["left_margin"] * s, df_row["top_margin"] * s))
            img_byte_arr = io.BytesIO()
            tmpimg.save(img_byte_arr, format='PNG')
            data[item] = img_byte_arr.getvalue()

    for file, content in data.items():
        archive.writestr("sprites/" + folder + "$" + scale + "/" + file, content)
    archive.writestr("sprites/" + folder + "$" + scale + ".json", create_animation_config(folder + "$" + scale, data.keys(), df))

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

def create_main_mod_config(scale):
    conf = {
        "author": "Ubisoft",
        "contact": "vcmi.eu",
        "description": "Resources (x" + scale + ")",
        "modType": "Graphical",
        "name": "HD (x" + scale + ")",
        "version": "1.0"
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)

def create_lang_mod_config(scale, language):
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
        "description": "Translated resources (x" + scale + ")",
        "modType": "Translation",
        "name": "HD Localisation (" + languages[language] + ") (x" + scale + ")",
        "version": "1.0",
        "language": languages[language]
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)

def create_animation_config(name, files, df):
    files = sorted(files)

    conf = {
        "basepath": name + "/",
        "images": [
            {
                "group": row["group"],
                "frame": row["frame"],
                "file": row["imagename"] + ".png"
            }
            for i, row in df.iterrows()
            if row["imagename"].upper() in [os.path.splitext(x)[0].upper() for x in files]
        ]
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)