import sqlite3
import helpers


class TmsuConnect():
    def __init__(self):
        self.connection = sqlite3.connect(".tmsu/db")
        self.cursor = self.connection.cursor()

    def get_tags(self):
        self.cursor.execute("SELECT * FROM tag")
        result = self.cursor.fetchall()
        tags = []
        for row in result:
            tags.append(TmsuTag(row))
        return tags

    def get_file_info(self, filename):
        pass

    def get_all_files(self):
        self.cursor.execute("SELECT * FROM file WHERE is_dir = 0")
        res = self.cursor.fetchall()
        all_files = []
        for row in res:
            all_files.append(TmsuFile(row))
        return all_files

    def check_if_tag_exists(self, new_tag):
        self.cursor.execute(f"SELECT ? from tag;", (new_tag,))
        res = self.cursor.fetchall()
        #print(res)
        return res != NULL

    def get_tags_for_file(self, file):
        """Takes a database connection and a TmsuFile object,
        returns a list of TmsuTag objects associated with this file."""
        fileid = file.id
        self.cursor.execute(f"""
                            SELECT tag.id, tag.name
                            FROM file_tag
                            INNER JOIN tag
                            ON file_tag.tag_id = tag.id
                            WHERE file_id = ? ;""", (file.id, ))

        res = self.cursor.fetchall()
        tags_for_file = []
        for row in res:
            tags_for_file.append(TmsuTag(row))
        return tags_for_file

    def get_files_for_tag(self, tag):
        tag_id = helpers.clean_name(tag.id)
        self.cursor.execute(f"""
                            SELECT file_tag.file_id
                            FROM file_tag
                            INNER JOIN tag
                            ON file_tag.tag_id = tag.id
                            WHERE tag_id = ?;""", (tag.id, ))
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


class TmsuFile():
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


class TmsuTag():
    def __init__(self, db_row):
        self.id = db_row[0]
        self.name = db_row[1]


