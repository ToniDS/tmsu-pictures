import sqlite3
from . import helpers
import os


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

    def get_all_files(self, all_times=True):
        if all_times:
            self.cursor.execute("SELECT * FROM file WHERE is_dir = 0")
        else:
            self.cursor.execute("""WITH exclude AS (
                                SELECT file_id
                                FROM file_tag
                                WHERE value_id IN (SELECT id FROM value))
                                SELECT *
                                FROM file
                                WHERE is_dir = 0 AND id NOT IN exclude""")
        res = self.cursor.fetchall()
        all_files = []
        for row in res:
            all_files.append(TmsuFile(row))
        return all_files

    def check_if_tag_exists(self, new_tag):
        self.cursor.execute("SELECT ? from tag;", (new_tag,))
        res = self.cursor.fetchall()
        # print(res)
        return res is not None

    def get_tags_for_file(self, file):
        """Takes a database connection and a TmsuFile object,
        returns a list of TmsuTag objects associated with this file."""
        self.cursor.execute("""
                            SELECT DISTINCT tag.id, tag.name
                            FROM file_tag
                            INNER JOIN tag
                            ON file_tag.tag_id = tag.id
                            WHERE file_id = ? ;""", (file.id, ))

        res = self.cursor.fetchall()
        tags_for_file = []
        for row in res:
            tags_for_file.append(TmsuTag(row))
        return tags_for_file

    def get_files_for_tag(self, tag, tags_to_exclude=None):
        if isinstance(tag, str):
            tag_name = helpers.clean_name(tag)
        else:
            tag_name = helpers.clean_name(tag.name)
        if tags_to_exclude:
            for i, tag in enumerate(tags_to_exclude):
                if isinstance(tags_to_exclude, str):
                    tags_to_exclude[i] = helpers.clean_name(tag)
        if not tags_to_exclude:
            self.cursor.execute("""
                            WITH FILEID AS (
                                SELECT file_tag.file_id
                                    FROM file_tag
                                    INNER JOIN tag
                                    ON file_tag.tag_id = tag.id
                                    WHERE name = ?)
                            SELECT file.id, directory, name,
                                fingerprint, mod_time, size, is_dir
                                FROM file INNER JOIN FILEID on
                                file.id = FILEID.file_id;""",
                                (tag_name,))
        else:
            tags = [tag_name] + tags_to_exclude
            self.cursor.execute(f"""
                            WITH fileid AS (
                                SELECT file_tag.file_id
                                    FROM file_tag
                                    INNER JOIN tag
                                    ON file_tag.tag_id = tag.id
                                    WHERE name = ?
                            ),
                            exclude AS (
                                SELECT file_tag.file_id
                                    FROM file_tag
                                    INNER JOIN tag
                                    ON file_tag.tag_id = tag.id
                                    WHERE name in
                                    ({",".join(['?']*len(tags_to_exclude))})
                            )

                            SELECT file.id, directory, name,
                                fingerprint, mod_time, size, is_dir
                                FROM file INNER JOIN (
                                    SELECT * FROM fileid EXCEPT
                                    SELECT * FROM exclude) AS files
                                ON
                                file.id = files.file_id;""",
                                (tags))
        res = self.cursor.fetchall()
        files_for_tag = []
        for row in res:
            files_for_tag.append(TmsuFile(row))
        return files_for_tag

    def add_new_tag(self, tag):
        raise NotImplementedError

    def add_new_tag_to_file(self, tag, file):
        raise NotImplementedError

    def close(self):
        self.connection.commit()
        self.connection.close()

    def check_if_file_in_db(self, filepath):
        self.cursor.execute("SELECT * FROM file WHERE is_dir = 0")
        res = self.cursor.fetchall()
        for picture in res:
            tm_file = TmsuFile(picture)
            if filepath == tm_file.get_file_path():
                return True
        return False


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
        return os.path.join(self.directory, self.name)


class TmsuTag():
    def __init__(self, db_row):
        self.id = db_row[0]
        self.name = db_row[1]


