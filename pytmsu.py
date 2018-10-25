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
    pretty_print_tags(tm)

    tags_from_last=[]
    for file in all_files:
        f_path = file.get_file_path()

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

            print_tags_for_file(tm, file)
            tags_assorted = []

            while True:
                prompt = '''
    * enter new tags, comma-separated or enter "quit" to quit program
    * or enter ls to see a list of tags for file
    * finish: ENTER
            '''
                if tags_from_last == []:
                    user = input(prompt)
                else:
                    user = helpers.rlinput(prompt,
                                           prefill=', '.join(tags_from_last))
                    tags_from_last = []



                if user is '':
                    p.terminate()
                    break
                elif user.strip() == 'quit':
                    helpers.clean_up(tm, p)
                    exit()
                elif user.strip() == 'ls':
                    current_tags = []
                    for tag in tm.get_tags_for_file(file):
                        current_tags.append(tag.name)
                    print(f"""File {f_path} has the following tags:
                          {', '.join(current_tags)}.""")
                else:
                    tags, tags_to_remove = helpers.parse_user_tags(user)
                    tags_assorted.extend(tags)
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
                            subprocess.Popen(['tmsu', 'tag', f_path, tag],
                                             stdin=subprocess.DEVNULL,
                                             stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL)
                        print(f"Added tags {' '.join(tags)} to file {f_path}")
                    if tags_to_remove:
                        for tag in tags_to_remove:
                            subprocess.Popen(['tmsu', 'untag', f_path, tag],
                                             stdin=subprocess.DEVNULL,
                                             stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL)
                        print(f"""Removed tags {' '.join(tags_to_remove)} from file {f_path}""")
            tags_from_last = tags_assorted
            # break out of while-loop showing the inputs
            break
    helpers.clean_up(tm, p)
    exit()

def pretty_print_tags(db_connection):
    tag_cnt = 0
    tag_string = ''
    for tag in db_connection.get_tags():
        tag_cnt += 1

        tag_string += tag.name + '    '
        if tag_cnt >= 5:
            print(tag_string)
            tag_cnt = 0
            tag_string = ''


def print_tags_for_file(db_connection, file):
    f_path = file.get_file_path()
    tags = db_connection.get_tags_for_file(file)
    tag_names = []
    # print(tags)
    for tag in tags:
        # print(tag.id)
        tag_names.append(tag.name)

    file_tags= ', '.join(tag_names)

    print(f"File {f_path} has the following tags: {file_tags}")


if __name__ == "__main__":
    main()
