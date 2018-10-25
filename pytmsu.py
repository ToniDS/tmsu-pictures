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

def main():
    tm = db.TmsuConnect()
    all_tagnames = []
    for tag in tm.get_tags():
        all_tagnames.append(tag.name)

    all_files = tm.get_all_files()
    print(f"The current database has { len(all_files) } files.")
    helpers.pretty_print_tags(tm)

    tags_from_last = []
    for file in all_files:
        f_path = file.get_file_path()
        tags_assorted = []

        # in order to not focus on the feh window, I have included something in my
        # i3 config
        # check if file exists in directory
        if os.path.isfile(f_path):
            p = subprocess.Popen(['feh', '--auto-zoom', '--scale-down', f_path],
                                stdin=subprocess.PIPE)
        else:
            continue

        while True:
            poll = p.poll()
            if poll is None:
                #print('RUNNING')
                pass
            else:
                #print('ENDED')
                print('NEXT')
                break

            helpers.print_tags_for_file(tm, file)

            # while True get input
            # while True:
            user = get_input(tags_from_last)

            # process input
            processed_input = process_input(user, p, file, tm)
            if not processed_input:
                break
            else:
                tags, tags_to_remove = processed_input

            # add tags
            add_tags(tags, tags_assorted, all_tagnames, f_path)
            # remove tags
            remove_tags(tags_to_remove, f_path)

        tags_from_last = tags_assorted


    helpers.clean_up(tm, p)
    exit()

def get_input(tags_from_last):
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



def process_input(input, feh_process, file, db):
    filepath = file.get_file_path()
    if input is '':
        feh_process.terminate()
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


def add_tags(tags, tags_assorted, all_tagnames, filepath):
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
        tags_assorted.extend(tags)

def remove_tags(tags_to_remove, filepath):
    if tags_to_remove:
        for tag in tags_to_remove:
            subprocess.Popen(['tmsu', 'untag', filepath, tag],
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        print(f"""Removed tags {' '.join(tags_to_remove)} from file {filepath}""")



if __name__ == "__main__":
    main()
