import sqlite3
import subprocess
import time
import sys
import os

def clean_name(some_var):
    """ Helper function to make variables usable in SQLite queries
    without risk of SQL injection vulnerability."""
    var = str(some_var)
    return ''.join(char for char in var if char.isalnum())


class tmsu_file():
    def __init__(self, db_row):
        self.id = db_row[0]
        self.directory = db_row[1]
        self.name = db_row[2]
        self.fingerprint = db_row[3]
        self.mod_time = db_row[4]
        self.size = db_row[5]
        self.is_dir = db_row[6]

    def get_file_path(self):
        return self.directory + '/' + self.name

class tmsu_tag():
    def __init__(self, db_row):
        self.id = db_row[0]
        self.name = db_row[1]

class tmsu_file_tag():
    def __init__(self, db_row):
        self.file_id = db_row[0]
        self.tag_id = db_row[1]
        self.value_id = db_row[2]



class tmsu_connect():
    def __init__(self):
        self.connection = sqlite3.connect(".tmsu/db")
        self.cursor = self.connection.cursor()

    def get_tags(self):
        self.cursor.execute("SELECT * FROM tag")
        result = self.cursor.fetchall()
        tags = []
        for row in result:
            tags.append(tmsu_tag(row))
        return tags

    def get_file_info(self, filename):
        # id =
        pass

    def get_all_files(self):
        self.cursor.execute("SELECT * FROM file WHERE is_dir = 0")
        res = self.cursor.fetchall()
        all_files = []
        for row in res:
            all_files.append(tmsu_file(row))
        return all_files

    def check_if_tag_exists(self, new_tag):
        new_tag = clean_name(new_tag)
        self.cursor.execute(f"SELECT {new_tag} from tag")
        res = self.cursor.fetchall()
        #print(res)
        return res != NULL

    def get_tags_for_file(self, file):
        """Takes a database connection and a tmsu_file object,
        returns a list of tmsu_tag objects associated with this file."""

        file_id = clean_name(file.id)
        ##directory = clean_name(filee.directory)

        self.cursor.execute(f"""
                            SELECT tag.id, tag.name
                            FROM file_tag
                            INNER JOIN tag
                            ON file_tag.tag_id = tag.id
                            WHERE file_id = {file_id}""")

        res = self.cursor.fetchall()
        tags_for_file = []
        for row in res:
            tags_for_file.append(tmsu_tag(row))
        return tags_for_file

    def get_files_for_tag(self, tag):
        tag_id = clean_name(tag.id)

        self.cursor.execute(f"""
                            SELECT file_tag.file_id
                            FROM file_tag
                            INNER JOIN tag
                            ON file_tag.tag_id = tag.id
                            WHERE tag_id = {tag_id}""")
        res = self.cursor.fetchall()
        files_for_tag = []
        for row in res:
            files_for_tag.append(row)
        return files_for_tag

    def add_new_tag(self, tag):
        pass

    def add_new_tag_to_file(self, tag, file):
        pass

    def close(self):
        self.connection.commit()
        self.connection.close()


tm = tmsu_connect()
#print(tm.get_tags())
##print(tm.get_all_files())
def main():
    tm = tmsu_connect()
    all_files = tm.get_all_files()
    print(f"The current database has {len(all_files)} files.")
    pretty_print_tags(tm)

    for file in all_files:
        f_path = file.get_file_path()
        #print(f_path)

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

            print_tags_for_file(file)

            while True:
                user = input('''
    * enter new tags, comma-separated
    * finish: ENTER
            ''')

                if user is '':
                    p.kill()
                    break
                else:
                    tags, tags_to_remove = parse_user_tags(user)
                    if len(tags) != 0:
                        subprocess.Popen(['tmsu', 'tag', '--', f_path, ' '.join(tags)])
                        print(f"Added tags {' '.join(tags)} to file {f_path}")
                    if len(tags_to_remove) != 0:
                        subprocess.Popen(['tmsu', 'untag', f_path,
                                        ' '.join(tags_to_remove)])
                        print(f"""Removed tags {' '.join(tags_to_remove)} from file
                            {f_path}""")

            break

def pretty_print_tags(db):
    tag_cnt = 0
    tag_string = ''
    for tag in db.get_tags():
        tag_cnt += 1

        tag_string += tag.name + '    '
        if tag_cnt >= 5:
            print(tag_string)
            tag_cnt = 0
            tag_string = ''


def print_tags_for_file(file):
    f_path = file.get_file_path()
    tags = tm.get_tags_for_file(file)
    tag_names = []
    # print(tags)
    for tag in tags:
        # print(tag.id)
        tag_names.append(tag.name)

    file_tags= ', '.join(tag_names)

    print(f"File {f_path} has the following tags: {file_tags}")


def parse_user_tags(input):
    tags = input.split(",")
    tags_to_remove = []
    for tag in tags:
        if tag[0] == "-":
            tags.remove(tag)
            tags_to_remove.append(tag)
    return tags, tags_to_remove






        #pass
    #sys.exit()

def clean_up(db_connection):
    """Check if there's tags without a file associated to them, then remove
    them from the database."""
    tags_to_remove=[]
    for tag in db_connection.get_tags():
        if len(tm.get_files_for_tag) == 0:
            tags_to_remove.append(tag.name)
    subprocess.Popen(['tmsu', 'delete', ' '.join(tags_to_remove)])
    db_connection.close()


#sql_command = """INSERT INTO employee (staff_number, fname, lname, gender, birth_date)
#    VALUES (NULL, "Frank", "Schiller", "m", "1955-08-17");"""
#cursor.execute(sql_command)

if __name__ == "__main__":
    main()
