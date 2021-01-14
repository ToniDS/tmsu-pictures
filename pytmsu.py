import sqlite3
import subprocess
import time
import sys
import os
import readline
import damlev
import database as db
import helpers
import speller
import argparse
import re
from glob import glob
from pathlib import Path
import datetime



def main():
    parser = argparse.ArgumentParser(description="image folder")
    parser.add_argument("folder", type = str)
    parser.add_argument("--tag", type=str, default=None, 
    help='Provide an optional tag')
    parser.add_argument("--exclude", type=str, default=None, nargs = "+")
    args = parser.parse_args()
    path = os.path.join("/home/toni", args.folder)
    search_tag = args.tag
    exclude_tag = args.exclude
    os.chdir(path)
    tm = db.TmsuConnect()
    all_tagnames = set()
    p = None
    for tag in tm.get_tags():
        all_tagnames.add(tag.name)
    folder = "Bilder_Kindheit" 
    #set_up_database(tm, path, folder)
    if tag: 
        all_files = tm.get_files_for_tag(search_tag, exclude_tag)
    else: 
        all_files = tm.get_all_files()
    print(all_files)
    print(f"The current database has { len(all_files) } files.")
    helpers.pretty_print_tags(tm)

    tags_from_last = []
    for i, file in enumerate(all_files):
        print(f"Processing file {i} of {len(all_files)}")
        f_path = file.get_file_path()
        tags_assorted = []

        file_tags = tm.get_tags_for_file(file)
      
        # in order to not focus on the feh window,
        # I have included something in my i3 config
        # check if file exists in directory
        if os.path.isfile(f_path):
            p = subprocess.Popen(['feh', '--auto-zoom', '--scale-down',
                                 f_path], stdin=subprocess.PIPE)
        else:
            continue

        helpers.print_tags_for_file(tm, file)
        
        while True:
            user = get_input(tags_from_last)
            processed_input = process_input(user, p, file, tm, tags_assorted, all_tagnames)
            if not processed_input:
                p.terminate()
                break
            else:
                tags, tags_to_remove = processed_input
            add_tags(tags, f_path, tags_assorted, all_tagnames)
            for tag in tags: 
                all_tagnames.add(tag)
            remove_tags(tags_to_remove, f_path)

        now = datetime.datetime.now()
        add_tags([f"edit-date={now.strftime('%Y-%m-%d')}"], f_path)

        tags_from_last = tags_assorted
        

    if p: 
        helpers.clean_up(tm, p)
    exit()


def get_input(tags_from_last):
    """Gets input from user"""
    prompt = '''
* enter new tags, comma-separated or enter "quit" to quit program
* or enter ls to see a list of tags for file
* finish: ENTER
'''
    if not tags_from_last:
        user = input(prompt)
    else:
        user = helpers.rlinput(prompt,
                               prefill=', '.join(tags_from_last))
        tags_from_last.clear()
    return user


def process_input(input, feh_process, file, db, tags_assorted, all_tagnames):
    filepath = file.get_file_path()
    now = datetime.datetime.now()
    if input == '':
        return
    elif input.strip() == 'quit':
        helpers.clean_up(db, feh_process)
        exit()
    elif input.strip() == 'ls':
        current_tags = []
        for tag in db.get_tags_for_file(file):
            current_tags.append(tag.name)
        print(f"""File {filepath} has the following tags:
                {', '.join(current_tags)}.""")
        return [], []
    else:
        tags, tags_to_remove = helpers.parse_user_tags(input)
        return tags, tags_to_remove


def add_tags(tags, filepath, tags_assorted = [], all_tagnames = []):
    """
    Method that adds {tags} to file
    """
    if tags:
        for tag in tags:
            suggestion = speller.spellcheck(tag, all_tagnames)
            if suggestion:
                prompt = f"""Did you mean the following tag? {suggestion}
                        y/N
                        """
                answer = input(prompt)
                if answer == 'yes' or answer == 'y':
                    tags.remove(tag)
                    tag = suggestion
                    tags.append(tag)
            subprocess.Popen(['tmsu', 'tag', filepath, tag],
                             stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        print(f"Added tags {' '.join(tags)} to file {filepath}")
        for tag in tags: 
            if "edit-date" not in tag:
                tags_assorted.append(tag)


def remove_tags(tags_to_remove, filepath):
    if tags_to_remove:
        for tag in tags_to_remove:
            subprocess.Popen(['tmsu', 'untag', filepath, tag],
                             stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        print(f"Removed tags {' '.join(tags_to_remove)} from file {filepath}")

def split(filepath):
    folder, filename = os.path.split(filepath)
    _, folder = os.path.split(folder)
    return folder, filename
    

def create_tag_from_folder(folder):
    tags = []
    comp = re.compile(r"\d{4}")
    if match := re.search(comp, folder):
        match = match[0]
        if int(match) > 1989 and int(match) < 2020:
            tags.append(match)
    possibilities = [
        "Abiball", 
        "Toni", 
        "Sommerfest",
        "Mentorenfreizeit", 
        "MengJing", 
        "Oberstufenball", 
        "Mama"]
    for name in possibilities: 
        if name.lower() in folder.lower(): 
            tags.append(name)
    return tags

def create_tags_from_file(filename):
    tags = []
    p = re.compile(r"\d{4}")
    if match := re.search(p, filename):
        match = match[0]
        if int(match) > 1989 and int(match) < 2020:
            tags.append(match)
    possibilities = ["Freya", "Toni", 
    "Sina", "Lena", "Luzia", "Helga", "Ritschy", "Tunesien", 
    "Wilhelma", "Hubert", "Horst", "Julia", "Krakau", "Mentorenfreizeit", 
    "Oberstufenball", "Bad Mergentheim", "Uttenhofen", "Sommerfest", "Spieleabend", 
    "Antonia", "Oma", "Mutter", "Rafik"]
    for name in possibilities: 
        if name.lower() in filename.lower(): 
            tags.append(name)
    return tags

def set_up_database(tm, path, folder=None): 
    all_files = []
    if folder: 
        path = os.path.join(path, folder)
    for dirpath, dirs, files in os.walk(path):
        for filename in files: 
            picture_ext = ("jpg", "JPG", "jpeg", "JPEG")
            if filename.endswith(picture_ext):
                all_files.append(os.path.join(dirpath, filename))

    for f_path in all_files:
        print(f"{f_path=}")
        #f_path = file.get_file_path()

        if not folder: 
            significant_path = os.path.split(f_path)[0]
        else: 
            head, tail = os.path.split(f_path)
            folder = os.path.split(head)[0]
            significant_path = os.path.join(folder, tail)
        if not tm.check_if_file_in_db(significant_path):
            folder, filename = split(f_path)
            tags = []
            if folder_tags:=create_tag_from_folder(folder):
                tags.extend(folder_tags)
            if filename_tags:=create_tags_from_file(filename):
                tags.extend(filename_tags)
            if not tags: 
                tags = ["Bilder"]
            add_tags(tags, f_path)
    

if __name__ == "__main__":
    main()