import sqlite3
import subprocess
import time
import sys

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
        self.cursor.execute(f"SELECT {new_tag} from tag")
        res = self.cursor.fetchall()
        return res != NULL

    def get_tags_for_file(self, file):
        t = (file.id, )
        self.cursor.execute("SELECT *"
                            "FROM (file_tag INNER JOIN tag"
                            "ON file_tag.tag_id = tag.id)"
                            "WHERE file_id = ?)", t)
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
    print(file.name)
    p = subprocess.Popen(['feh', '--auto-zoom', '--scale-down', fPath])
    #subprocess.check_call(shell=True)

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
        print(tags)
        for tag in tags:
            print(tag.id)
            tag_names.append(tag.name)

        file_tags= ', '.join(tag_names)

        print(f"File {fPath} has the following tags: {file_tags}")

        user = input('''
        * enter new or existing tag
        * finish: ENTER
        ''')

        if user is '':
            p.kill()
            break
        else:
            #TODO: ADD TAGs HERE!
            # first, parse tag
            tags = user.split(",")
            for tag in tags:
                if tm.check_if_tag_exists(tag):
                    pass


        #pass
    #sys.exit()


#sql_command = """INSERT INTO employee (staff_number, fname, lname, gender, birth_date)
#    VALUES (NULL, "Frank", "Schiller", "m", "1955-08-17");"""
#cursor.execute(sql_command)
