import subprocess
import sys
import os
from . import helpers
from .database import TmsuConnect
from .ProcessedInput import ProcessedInput
from .TagManager import TagManager
from .export import export_files
import argparse
import re
import datetime


def main():
    parser = argparse.ArgumentParser(description="image folder")
    parser.add_argument("folder", type=str)
    parser.add_argument("--tag", type=str, default=None,
                        help='Provide an optional tag')
    parser.add_argument("--exclude", type=str, default=None,
                        nargs="+")
    parser.add_argument("--all", action='store_true')
    parser.add_argument("--init", action='store_true')
    parser.add_argument("--export", action="store_true")

    args = parser.parse_args()
    # TODO: Make sure that if I export, all is the other way around. Standard: export those that have been edited
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

    if not tm.connection:
        new_database = input("Do you want to create a new database? \n y/N\n")
        if new_database == "y":
            p = subprocess.run(["tmsu", "init"])
            if p.returncode == 0:
                tm.connect_database()
        else:
            exit()

    if args.init:
        print("Setting up database")
        set_up_database(tm, path)

    if search_tag:
        all_files = tm.get_files_for_tag(search_tag, exclude_tag)
    else:
        all_files = tm.get_all_files(all_times=all_times)

    print(f"The current database has { len(all_files) } files.")
    helpers.pretty_print_tags(tm)

    # first step: export_all
    if args.export:
        export_files(tm, all_files)
        exit()

    tags_from_last = []
    viewer_process = None
    tagmanager = TagManager(tm)
    for i, tmsu_file in enumerate(all_files):
        tagmanager.next_image()

        print(f"Processing file {i} of {len(all_files)}")
        f_path = tmsu_file.get_file_path()
        tags_assorted = []

        # in order to not focus on the feh window,
        # I have included something in my i3 config
        # check if file exists in directory
        if not os.path.isfile(f_path):
            continue

        viewer_process = subprocess.Popen(
            ['feh', '--auto-zoom', '--scale-down', f_path],
            stdin=subprocess.PIPE
        )

        helpers.print_tags_for_file(tm, tmsu_file)

        while True:
            user = get_input(tags_from_last)
            processed_input = process_input(user, tmsu_file)
            if processed_input.state == ProcessedInput.STATE_NEXT_IMAGE:
                viewer_process.terminate()
                break
            elif processed_input.state == ProcessedInput.STATE_LIST_TAGS:
                print_tags_for_file(tm, tmsu_file)
                print_edit_date(tm, tmsu_file)
                continue
            elif processed_input.state == ProcessedInput.STATE_EXIT:
                helpers.clean_up(tm, viewer_process)
                sys.exit(0)
            elif processed_input.state == ProcessedInput.STATE_MODIFY_TAGS:
                # tags_to_add, tags_to_remove = processed_input.get_tags()
                # add_tags(tags_to_add, f_path, tags_assorted, all_tagnames)
                # remove_tags(tags_to_remove, f_path)
                tagmanager.manage(f_path, processed_input.user_input)
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
        user_input = helpers.rlinput(
            prompt,
            prefill=', '.join(tags_from_last)
        )
        tags_from_last.clear()
    return user_input


def process_input(user_input, tmsu_file):
    processed_input = ProcessedInput()
    if user_input == '':
        processed_input.state = ProcessedInput.STATE_NEXT_IMAGE
    elif user_input.strip() == 'quit':
        processed_input.state = ProcessedInput.STATE_EXIT
    elif user_input.strip() == 'ls':
        processed_input.state = ProcessedInput.STATE_LIST_TAGS
    else:
        # tags_to_add, tags_to_remove = helpers.parse_user_tags(user_input)
        processed_input.state = ProcessedInput.STATE_MODIFY_TAGS
        processed_input.user_input = user_input
        # processed_input.tags_to_add = tags_to_add
        # processed_input.tags_to_remove = tags_to_remove
    return processed_input


def print_tags_for_file(db, tmsu_file):
    """Prints the tags already assigned to file in the database."""
    current_tags = []
    for tag in db.get_tags_for_file(tmsu_file):
        current_tags.append(tag.name)
    print(f"""File {tmsu_file.get_file_path()} has the following tags:
{', '.join(current_tags)}.""")


def print_edit_date(tm, tmsu_file):
    """Prints the newest edit date fo file if edit_date is set."""
    edit_date = tm.get_latest_edit_date(tmsu_file)
    if edit_date:
        print(f"edit-date: {edit_date}")


def add_tags(tags, filepath):
    """
    Method that adds {tags} to file
    """

    if not tags:
        return
    args = ['tmsu', 'tag', filepath] + tags
    subprocess.run(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"Added tags {' '.join(tags)} to file {filepath}")


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
    tags = set()
    comp = re.compile(r"\d{4}")
    if match := re.search(comp, folder):
        match = match[0]
        if 1989 < int(match) < 2020:
            tags.add(match)
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
            tags.add(name)
    return tags


def create_tags_from_file(filename: str):
    """Does not work, currently never called."""
    tags = get_year_tags(filename)
    possibilities = [
        "Freya", "Toni",
        "Sina", "Lena", "Luzia", "Helga", "Ritschy", "Tunesien",
        "Wilhelma", "Hubert", "Horst", "Julia", "Krakau", "Mentorenfreizeit",
        "Oberstufenball", "Bad Mergentheim", "Uttenhofen", "Sommerfest",
        "Spieleabend", "Antonia", "Oma", "Mutter", "Rafik"
    ]
    for name in possibilities:
        if name.lower() in filename.lower():
            tags.add(name)
    return tags


def get_year_tags(filename: str):
    tags = set()
    regex_year = re.compile(r"\d{4}")
    if year := re.search(regex_year, filename):
        year = year[0]
        if 1989 < int(year) < 2020:
            tags.add(year)
    return tags


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

        if not folder:
            significant_path = os.path.split(f_path)[0]
        else:
            head, tail = os.path.split(f_path)
            folder = os.path.split(head)[0]
            significant_path = os.path.join(folder, tail)
        if not tm.check_if_file_in_db(significant_path):
            folder, filename = split(f_path)
            tags = []
            if folder_tags := create_tag_from_folder(folder):
                tags.extend(folder_tags)
            if filename_tags := create_tags_from_file(filename):
                tags.extend(filename_tags)
            if not tags:
                tags = ["Bilder"]
            add_tags(tags, f_path)


if __name__ == "__main__":
    main()
