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


class tmsuFile():
    def __init__(self, dbRow):
        self.id = dbRow[0]
        self.directory = dbRow[1]
        self.name = dbRow[2]
        self.fingerprint = dbRow[3]
        self.mod_time = dbRow[4]
        self.size = dbRow[5]
        self.is_dir = dbRow[6]

    def getFilePath(self):
        return self.directory + '/' + self.name

class tmsuTag():
    def __init__(self, dbRow):
        self.id = dbRow[0]
        self.name = dbRow[1]

class tmsuFileTag():
    def __init__(self, dbRow):
        self.file_id = dbRow[0]
        self.tag_id = dbRow[1]
        self.value_id = dbRow[2]



class tmsuConnect():
    def __init__(self):
        self.connection = sqlite3.connect(".tmsu/db")
        self.cursor = self.connection.cursor()

    def getTags(self):
        self.cursor.execute("SELECT * FROM tag")
        result = self.cursor.fetchall()
        return result

    def getFileInfo(self, filename):
        # id =
        pass

    def getAllFiles(self):
        self.cursor.execute("SELECT * FROM file WHERE is_dir = 0")
        res = self.cursor.fetchall()
        allFiles = []
        for row in res:
            allFiles.append(tmsuFile(row))
        return allFiles

    def check_if_tag_exists(self, new_tag):
        new_tag = clean_name(new_tag)
        self.cursor.execute(f"SELECT {new_tag} from tag")
        res = self.cursor.fetchall()
        #print(res)
        return res != NULL

    def get_tags_for_file(self, file):
        """Takes a database connection and a tmsuFile object,
        returns a list of tmsuTag objects associated with this file."""

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
            tags_for_file.append(tmsuTag(row))
        return tags_for_file

    def add_new_tag(self, tag):
        pass

    def add_new_tag_to_file(self, tag, file):
        pass

    def close(self):
        self.connection.commit()
        self.connection.close()


tm = tmsuConnect()
#print(tm.getTags())
##print(tm.getAllFiles())

tagCnt = 0
tagString = ''
for tag in tm.getTags():
    tagCnt += 1

    tagString += tag[1] + '    '
    if tagCnt >= 5:
        print(tagString)
        tagCnt = 0
        tagString = ''




allFiles = tm.getAllFiles()
for file in allFiles:
    fPath = file.getFilePath()
    #print(fPath)

    # in order to not focus on the feh window, I have included something in my
    # i3 config
    # check if file exists in directory
    if os.path.isfile(fPath):
        p = subprocess.Popen('feh --auto-zoom --scale-down ' + fPath, shell=True,
                             stdin=subprocess.PIPE)
    #subprocess.check_call(shell=True)
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

        tags = tm.get_tags_for_file(file)
        tag_names = []
        # print(tags)
        for tag in tags:
            # print(tag.id)
            tag_names.append(tag.name)

        file_tags= ', '.join(tag_names)

        print(f"File {fPath} has the following tags: {file_tags}")


        while True:
            user = input('''
* enter new tags, comma-separated
* finish: ENTER
        ''')

            if user is '':
                p.kill()
                break
            else:
            #TODO: ADD TAGs HERE!
            # first, parse tag
                tags = user.split(",")
                subprocess.Popen('tmsu tag ' + fPath +' ' +' '.join(tags), shell=True)
                print(f"Added tags {' '.join(tags)} to file {fPath}")

        break


        #pass
    #sys.exit()


#sql_command = """INSERT INTO employee (staff_number, fname, lname, gender, birth_date)
#    VALUES (NULL, "Frank", "Schiller", "m", "1955-08-17");"""
#cursor.execute(sql_command)
