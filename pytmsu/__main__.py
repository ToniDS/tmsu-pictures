import sqlite3
import subprocess
import time
import sys
import os
import readline
from . import damlev, speller, helpers
from .database import TmsuConnect
from .ProcessedInput import ProcessedInput
from .TagManager import TagManager
import argparse
import re
from glob import glob
from pathlib import Path
import datetime
from textwrap import dedent


def main():
    parser = argparse.ArgumentParser(description="image folder")
    parser.add_argument("folder", type = str)
    parser.add_argument("--tag", type=str, default=None, 
                        help='Provide an optional tag')
    parser.add_argument("--exclude", type=str, default=None, 
                        nargs = "+")
    parser.add_argument("--all")

    args = parser.parse_args()
    if args.all: 
        all_times = True
    else: 
        all_times = False
    # TODO: Change to generic home path
    path = os.path.join("/home/toni", args.folder)
    search_tag = args.tag
    exclude_tag = args.exclude
    os.chdir(path)
    
    tm = TmsuConnect()
    
    #folder = "Bilder_Kindheit" 
    #set_up_database(tm, path, folder)
    if search_tag: 
        all_files = tm.get_files_for_tag(search_tag, exclude_tag)
    else: 
        all_files = tm.get_all_files(all_times=all_times)
    #print(all_files)
    print(f"The current database has { len(all_files) } files.")
    helpers.pretty_print_tags(tm)
    
    tags_from_last = []
    viewer_process = None
    for i, tmsu_file in enumerate(all_files):
        print(f"Processing file {i} of {len(all_files)}")
        f_path = tmsu_file.get_file_path()
        tags_assorted = []

        # in order to not focus on the feh window,
        # I have included something in my i3 config
        # check if file exists in directory
        if not os.path.isfile(f_path):
            continue

        file_tags = tm.get_tags_for_file(tmsu_file)
        viewer_process = subprocess.Popen(['feh', '--auto-zoom', '--scale-down',
                                 f_path], stdin=subprocess.PIPE)

        helpers.print_tags_for_file(tm, tmsu_file)
        
        while True:
            user = get_input(tags_from_last)
            processed_input = process_input(user, tmsu_file)
            if processed_input.state == ProcessedInput.STATE_NEXT_IMAGE:
                viewer_process.terminate()
                break
            elif processed_input.state == ProcessedInput.STATE_LIST_TAGS:
                print_tags_for_file(tm, tmsu_file)
                continue
            elif processed_input.state == ProcessedInput.STATE_EXIT:
                helpers.clean_up(tm, viewer_process)
                sys.exit(0)
            elif processed_input.state == ProcessedInput.STATE_MODIFY_TAGS:
                tags_to_add, tags_to_remove = processed_input.get_tags()
                add_tags(tags_to_add, f_path, tags_assorted, all_tagnames)
                remove_tags(tags_to_remove, f_path)
            else: 
                raise Exception(f"Unknown state: {processed_input.state}")

        now = datetime.datetime.now()
        add_tags([f"edit-date={now.strftime('%Y-%m-%d')}"], f_path)

        tags_from_last = tags_assorted

    if viewer_process: 
        helpers.clean_up(tm, viewer_process)
    exit()


def get_input(tags_from_last):
    """Gets input from user"""
    
    prompt = '''
* enter new tags, comma-separated or enter "quit" to quit program
* or enter ls to see a list of tags for file
* finish: ENTER
'''

    if not tags_from_last:
        user_input = helpers.rlinput(prompt, prefill="")
    else:
        user_input = helpers.rlinput(prompt,
                               prefill=', '.join(tags_from_last))
        tags_from_last.clear()
    return user_input


def process_input(user_input, tmsu_file):
    processed_input = ProcessedInput()
    filepath = tmsu_file.get_file_path()
    if user_input == '':
        processed_input.state = ProcessedInput.STATE_NEXT_IMAGE
    elif user_input.strip() == 'quit':
        processed_input.state = ProcessedInput.STATE_EXIT
    elif user_input.strip() == 'ls':
        processed_input.state = ProcessedInput.STATE_LIST_TAGS
    else:  
        tags_to_add, tags_to_remove = helpers.parse_user_tags(user_input)
        processed_input.state = ProcessedInput.STATE_MODIFY_TAGS
        processed_input.tags_to_add = tags_to_add
        processed_input.tags_to_remove = tags_to_remove
    return processed_input


def print_tags_for_file(db, tmsu_file):
    """Prints the tags already assigned to file in the database."""
    current_tags = []
    for tag in db.get_tags_for_file(tmsu_file):
        current_tags.append(tag.name)
    print(f"""File {tmsu_file.get_file_path()} has the following tags:
{', '.join(current_tags)}.""")


def add_tags(tags, filepath, tags_assorted = None, all_tagnames = None):
    """
    Method that adds {tags} to file
    """
    if tags_assorted is None: 
        tags_assorted = []
    if all_tagnames is None:
        all_tagnames = set()
    #Option
    if not tags: 
        return
    for tag in tags:
        suggestion = speller.spellcheck(tag, all_tagnames)
        if suggestion:
            prompt = f"""Did you mean the following tag? {suggestion}
                    y/N
                    """
            answer = input(prompt)
            if answer in ['yes', 'y']:
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


def remove_tags(tags_to_remove: list, filepath: str):
    if tags_to_remove:
        for tag in tags_to_remove:
            subprocess.Popen(['tmsu', 'untag', filepath, tag],
                             stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        print(f"Removed tags {' '.join(tags_to_remove)} from file {filepath}")

def split(filepath: str):
    folder, filename = os.path.split(filepath)
    _, folder = os.path.split(folder)
    return folder, filename
    

def create_tag_from_folder(folder: str):
    tags = []
    comp = re.compile(r"\d{4}")
    if match := re.search(comp, folder):
        match = match[0]
        if 1989 < int(match) < 2020:
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

def create_tags_from_file(filename: str):
    check_year
    possibilities = ["Freya", "Toni", 
    "Sina", "Lena", "Luzia", "Helga", "Ritschy", "Tunesien", 
    "Wilhelma", "Hubert", "Horst", "Julia", "Krakau", "Mentorenfreizeit", 
    "Oberstufenball", "Bad Mergentheim", "Uttenhofen", "Sommerfest", "Spieleabend", 
    "Antonia", "Oma", "Mutter", "Rafik"]
    for name in possibilities: 
        if name.lower() in filename.lower(): 
            tags.append(name)
    return tags

def check_year(filename: str):
    tags = []
    regex_year = re.compile(r"\d{4}")
    if year := re.search(regex_year, filename):
        year = year[0]
        if 1989 < int(year) < 2020:
            tags.append(year)


def set_up_database(tm: TmsuConnect, path: str, folder=None): 
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